# Local Imports
import os
from time import sleep

from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.enums import network_type
from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_MODEL_COMMANDS
from crawler.crawler_instance.proxies.i2p_controller.i2p_controller import i2p_controller
from crawler.crawler_instance.proxies.i2p_controller.i2p_enums import I2P_COMMANDS
from crawler.crawler_instance.proxies.shared_proxy_methods import shared_proxy_methods
from crawler.crawler_instance.proxies.tor_controller.tor_controller import tor_controller
from crawler.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler.crawler_services.mongo_manager.mongo_enums import MONGO_CRUD, MONGODB_COMMANDS
from crawler.crawler_services.shared.env_handler import env_handler
from crawler.crawler_services.shared.helper_method import helper_method
from crawler.crawler_services.shared.scheduler import RepeatedTimer
from crawler.crawler_services.shared.web_request_handler import webRequestManager
from crawler.crawler_instance.proxies.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_services.log_manager.log_controller import log
from crawler.crawler_services.request_manager.request_handler import request_handler

class crawl_model(request_handler):

  def __init__(self):
    self.__celery_vid = 100000
    self.__mongo = mongo_controller()


  @staticmethod
  def init_parsers():
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

    thread_count = env_handler.get_instance().env('CELERY_WORKER_COUNT')

    log.g().i(MANAGE_MESSAGES.S_INSTALL_LIVE_URL_STARTED + " : " + CRAWL_SETTINGS_CONSTANTS.S_FEEDER_URL_UNIQUE)
    web_request_manager = webRequestManager()
    m_proxy, m_tor_id = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_PROXY, [])

    mongo_response = self.__mongo.invoke_trigger(MONGO_CRUD.S_READ,[MONGODB_COMMANDS.S_GET_CRAWLABLE_URL_DATA, [None], [None]])
    m_live_url_list = []
    if shared_proxy_methods.get_onion_status() and mongo_response:
      for document in mongo_response:
        if len(document.keys())>0:
          m_live_url_list.append(document["m_url"])
          m_live_url_list = m_live_url_list[0: int(thread_count)]

    if shared_proxy_methods.get_i2p_status():
      i2p_urls = i2p_controller.get_instance().invoke_trigger(I2P_COMMANDS.S_FETCH)
      m_live_url_list.extend(i2p_urls)

    self.__mongo.invoke_trigger(MONGO_CRUD.S_UPDATE,[MONGODB_COMMANDS.S_RESET_CRAWLABLE_URL, [None], [False]])

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

    log.g().s(MANAGE_MESSAGES.S_INSTALLED_STARTED)
    install_urls, set_non_crawlable_urls = [], []
    for m_url in (helper_method.on_clean_url(url) for url in m_response_list):
      if helper_method.is_uri_validator(m_url) and m_url not in m_live_url_list:
        install_urls.append(m_url)
        m_updated_url_list.append(m_url)
      else:
        set_non_crawlable_urls.append(m_url)

    if install_urls:
      self.__mongo.invoke_trigger(MONGO_CRUD.S_UPDATE_BULK, [MONGODB_COMMANDS.S_INSTALL_CRAWLABLE_URL, install_urls, [True] * len(install_urls)])
    if set_non_crawlable_urls:
      self.__mongo.invoke_trigger(MONGO_CRUD.S_UPDATE_BULK, [MONGODB_COMMANDS.S_SET_CRAWLABLE_URL, set_non_crawlable_urls, [False] * len(set_non_crawlable_urls)])
    log.g().s(MANAGE_MESSAGES.S_INSTALLED_URL)


    self.__mongo.invoke_trigger(MONGO_CRUD.S_DELETE, [MONGODB_COMMANDS.S_REMOVE_DEAD_CRAWLABLE_URL, [list(m_live_url_list)], [None]])
    log.g().i(MANAGE_MESSAGES.S_INSTALL_LIVE_URL_FINISHED)

    return m_live_url_list, m_updated_url_list

  def __init_docker_request(self):
    m_live_url_list, m_updated_url_list = self.__install_live_url()
    m_list = list(m_live_url_list)
    m_list.extend(m_updated_url_list)
    self.__start_docker_request(m_list)

  def __init_direct_request(self):
    from crawler.crawler_instance.genbot_service.genbot_controller import genbot_instance
    log.g().i(MANAGE_MESSAGES.S_REINITIALIZING_CRAWLABLE_URL)

    while True:
      m_live_url_list, p_fetched_url_list = self.__install_live_url()
      m_request_list = list(m_live_url_list) + p_fetched_url_list

      for m_url_node in m_request_list:
        if helper_method.get_network_type(m_url_node) == network_type.I2P and shared_proxy_methods.get_i2p_status() or helper_method.get_network_type(m_url_node) == network_type.ONION and shared_proxy_methods.get_onion_status():
          m_proxy, m_tor_id = shared_proxy_methods.get_proxy(m_url_node)
          genbot_instance(m_url_node, -1, m_proxy, m_tor_id)

  def __reinit_docker_request(self):
    m_live_url_list, m_updated_url_list = self.__install_live_url()
    return m_updated_url_list

  def __start_docker_request(self, p_fetched_url_list):
    from crawler.crawler_services.celery_manager.celery_enums import CELERY_COMMANDS
    from crawler.crawler_services.celery_manager.celery_controller import celery_controller
    from crawler.shared_data import celery_shared_data

    if celery_shared_data.get_instance().get_network_status:
      while len(p_fetched_url_list) > 0:
        self.__celery_vid += 1
        try:
          m_url_node = p_fetched_url_list.pop(0)
          celery_controller.get_instance().invoke_trigger(CELERY_COMMANDS.S_START_CRAWLER, [m_url_node, self.__celery_vid])
        except Exception as ex:
          print(ex, flush=True)
          pass

    RepeatedTimer(CRAWL_SETTINGS_CONSTANTS.S_UPDATE_STATUS_TIMEOUT, self.reinit_list_periodically, False, p_fetched_url_list)

  def reinit_list_periodically(self, p_fetched_url_list):
    from crawler.shared_data import celery_shared_data
    from crawler.crawler_services.celery_manager.celery_controller import celery_controller
    from crawler.crawler_services.celery_manager.celery_enums import CELERY_COMMANDS

    if celery_shared_data.get_instance().get_network_status:
      if not p_fetched_url_list:
        p_fetched_url_list.extend(self.__reinit_docker_request())
      while len(p_fetched_url_list) > 0:
        self.__celery_vid += 1
        m_url_node = p_fetched_url_list.pop(0)
        celery_controller.get_instance().invoke_trigger(CELERY_COMMANDS.S_START_CRAWLER, [m_url_node, self.__celery_vid])

  def __init_crawler(self):
    self.__celery_vid = 100000

    if shared_proxy_methods.get_onion_status() or shared_proxy_methods.get_i2p_status():
      self.init_parsers()
      if APP_STATUS.DOCKERIZED_RUN:
       self.__init_docker_request()
      else:
       self.__init_direct_request()

  def invoke_trigger(self, p_command, p_data=None):
    if p_command == CRAWL_MODEL_COMMANDS.S_INIT:
      self.__init_crawler()
