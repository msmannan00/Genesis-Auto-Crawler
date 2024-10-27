# Local Imports
import os
from time import sleep

from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_MODEL_COMMANDS
from crawler.crawler_instance.genbot_service.genbot_controller import genbot_instance
from crawler.crawler_instance.genbot_service.genbot_unique_controller import prepare_and_fetch_data
from crawler.crawler_services.helper_services.helper_method import helper_method
from crawler.crawler_services.web_request_handler import webRequestManager
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_services.crawler_services.celery_manager.celery_enums import CELERY_COMMANDS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS, MONGO_CRUD
from crawler.crawler_services.helper_services.scheduler import RepeatedTimer
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_services.crawler_services.celery_manager.celery_controller import celery_controller
from crawler.shared_data import celery_shared_data

class crawl_model(request_handler):

  def __init__(self):
    self.__celery_vid = 100000
    self.__mongo = mongo_controller()


  def init_parsers(self):
    log.g().s(MANAGE_MESSAGES.S_PARSER_LOAD_STARTED)
    zip_path = "data.zip"
    extract_dir = os.path.join(os.getcwd(), CRAWL_SETTINGS_CONSTANTS.S_PARSE_EXTRACTION_DIR)
    web_request_manager = webRequestManager()

    try:
      file_content, status_or_error = web_request_manager.request_server_get(CRAWL_SETTINGS_CONSTANTS.S_PARSERS_URL)
      if os.path.exists(zip_path):
        os.remove(zip_path)
      if status_or_error == 200:
        with open(zip_path, "wb") as file:
          file.write(file_content)

        helper_method.extract_zip(zip_path, extract_dir)
      if os.path.exists(zip_path):
        os.remove(zip_path)
    except Exception as e:
      log.g().e(MANAGE_MESSAGES.S_PARSER_LOAD_EXCEPTION + " : " + str(e))
    finally:
      log.g().s(MANAGE_MESSAGES.S_PARSER_LOAD_FINISHED)


  # Start Crawler Manager
  def __install_live_url(self):
    log.g().i(MANAGE_MESSAGES.S_INSTALL_LIVE_URL_STARTED + " : " + CRAWL_SETTINGS_CONSTANTS.S_FEEDER_URL_UNIQUE)
    web_request_manager = webRequestManager()
    m_proxy, m_tor_id = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_PROXY, [])

    mongo_response = self.__mongo.invoke_trigger(MONGO_CRUD.S_READ,[MONGODB_COMMANDS.S_GET_CRAWLABLE_URL_DATA, [None], [None]])
    self.__mongo.invoke_trigger(MONGO_CRUD.S_UPDATE,[MONGODB_COMMANDS.S_RESET_CRAWLABLE_URL, [None], [False]])
    m_live_url_list = list([x['m_url'] for x in mongo_response])

    while True:
      try:
        m_html, m_status = web_request_manager.request_server_get(CRAWL_SETTINGS_CONSTANTS.S_FEEDER_URL_UNIQUE, m_proxy)
        if isinstance(m_html, bytes):
          m_html = m_html.decode('utf-8')
        if m_status == 200:
          break
        else:
          log.g().w(MANAGE_MESSAGES.S_INSTALL_LIVE_URL_TIMEOUT + " :: " + m_status + " :: " + CRAWL_SETTINGS_CONSTANTS.S_FEEDER_URL_UNIQUE)
      except Exception as ex:
        log.g().w(MANAGE_MESSAGES.S_INSTALL_LIVE_URL_TIMEOUT + " : " + ex)
      sleep(1)

    m_response_text = m_html

    m_response_list = m_response_text.splitlines()
    m_updated_url_list = []

    counter = 0
    for m_server_url in m_response_list:
      m_url = helper_method.on_clean_url(m_server_url)

      self.__mongo.invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_SET_CRAWLABLE_URL, [m_server_url], [False]])
      if helper_method.is_uri_validator(m_server_url) and m_url not in m_live_url_list:
        self.__mongo.invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_INSTALL_CRAWLABLE_URL, [m_url], [True]])
        m_updated_url_list.append(m_url)

      counter += 1
      if counter % 500 == 0:
        log.g().s(MANAGE_MESSAGES.S_INSTALLED_URL + " : " + m_url)

    self.__mongo.invoke_trigger(MONGO_CRUD.S_DELETE, [MONGODB_COMMANDS.S_REMOVE_DEAD_CRAWLABLE_URL, [list(m_live_url_list)], [None]])
    log.g().i(MANAGE_MESSAGES.S_INSTALL_LIVE_URL_FINISHED + " : " + CRAWL_SETTINGS_CONSTANTS.S_FEEDER_URL_UNIQUE)
    return m_live_url_list, m_updated_url_list

  def __init_docker_request(self):
    m_live_url_list, m_updated_url_list = self.__install_live_url()
    m_list = list(m_live_url_list)
    m_list.extend(m_updated_url_list)
    self.__start_docker_request(m_list)

  def __init_direct_request(self):
    log.g().i(MANAGE_MESSAGES.S_REINITIALIZING_CRAWLABLE_URL)

    while True:
      m_live_url_list, p_fetched_url_list = self.__install_live_url()
      m_request_list = list(m_live_url_list) + p_fetched_url_list
      for m_url_node in m_request_list:
        m_proxy, m_tor_id = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_PROXY, [])
        genbot_instance(m_url_node, -1, m_proxy, m_tor_id)

  def __reinit_docker_request(self):
    m_live_url_list, m_updated_url_list = self.__install_live_url()
    return m_updated_url_list

  def __start_docker_request(self, p_fetched_url_list):
    if celery_shared_data.get_instance().get_network_status:
      while len(p_fetched_url_list) > 0:
        self.__celery_vid += 1
        try:
          celery_controller.get_instance().invoke_trigger(CELERY_COMMANDS.S_START_CRAWLER, [p_fetched_url_list.pop(0), self.__celery_vid])
        except Exception as ex:
          print(ex, flush=True)
          pass

    RepeatedTimer(CRAWL_SETTINGS_CONSTANTS.S_UPDATE_STATUS_TIMEOUT, self.reinit_list_periodically, False, p_fetched_url_list)

  def reinit_list_periodically(self, p_fetched_url_list):
    if celery_shared_data.get_instance().get_network_status:
      if not p_fetched_url_list:
        p_fetched_url_list.extend(self.__reinit_docker_request())
      while len(p_fetched_url_list) > 0:
        self.__celery_vid += 1
        celery_controller.get_instance().invoke_trigger(CELERY_COMMANDS.S_START_CRAWLER, [p_fetched_url_list.pop(0), self.__celery_vid])

  def reinit_unique_feeders_periodically(self):
    log.g().i(MANAGE_MESSAGES.S_REINIT_UNIQUE_URL)

    content_list = prepare_and_fetch_data(CRAWL_SETTINGS_CONSTANTS.S_FEEDER_URL)
    celery_controller.get_instance().invoke_trigger(CELERY_COMMANDS.S_INVOKE_UNIQUE_CRAWLER, content_list)

  def __init_crawler(self):
    self.__celery_vid = 100000
    self.init_parsers()

    if CRAWL_SETTINGS_CONSTANTS.S_ALLOW_UNIQUE_FEEDER_UPDATES:
      RepeatedTimer(CRAWL_SETTINGS_CONSTANTS.S_UPDATE_UNIQUE_FEEDER_TIMEOUT, self.reinit_unique_feeders_periodically,True)

    if APP_STATUS.DOCKERIZED_RUN:
     self.__init_docker_request()
    else:
     self.__init_direct_request()

  def invoke_trigger(self, p_command, p_data=None):
    if p_command == CRAWL_MODEL_COMMANDS.S_INIT:
      self.__init_crawler()
