# Local Imports
import gc
import json
from asyncio import sleep
import os
import sys

from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_instance.genbot_service.parse_controller import parse_controller
from crawler.crawler_instance.local_shared_model.url_model import url_model, url_model_init
from crawler.crawler_services.crawler_services.elastic_manager.elastic_controller import elastic_controller
from crawler.crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CRUD_COMMANDS, ELASTIC_REQUEST_COMMANDS, ELASTIC_CONNECTIONS
from crawler.crawler_services.crawler_services.topic_manager.topic_classifier_controller import topic_classifier_controller
from crawler.crawler_services.crawler_services.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_COMMANDS
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_instance.genbot_service.genbot_enums import ICRAWL_CONTROLLER_COMMANDS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CRUD
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_COMMANDS
from crawler.crawler_services.web_request_handler import webRequestManager
from crawler.crawler_services.helper_services.duplication_handler import duplication_handler
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_services.helper_services.helper_method import helper_method


class genbot_controller(request_handler):

  hashseed = os.getenv('PYTHONHASHSEED')
  if not hashseed:
    os.environ['PYTHONHASHSEED'] = '0'
    os.execv(sys.executable, [sys.executable] + sys.argv)

  def __init__(self):
    self.__task_id = None
    self.m_url_duplication_handler = duplication_handler()
    self.__m_web_request_handler = webRequestManager()
    self.__m_html_parser = parse_controller()

    self.__m_tor_id = - 1
    self.__m_depth = 0
    self.m_unparsed_url = []
    self.m_parsed_url = []
    self.__m_proxy = {}

  def init(self, p_proxy, p_tor_id):
    self.__m_proxy, self.__m_tor_id = p_proxy, p_tor_id

  def __trigger_url_request(self, p_request_model: url_model):
    try:
      log.g().i(MANAGE_MESSAGES.S_PARSING_STARTING + " : " + str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + p_request_model.m_url)
      m_redirected_url, m_response, m_raw_html = self.__m_web_request_handler.load_url(p_request_model.m_url, self.__m_proxy)

      if m_response is True:

        m_parsed_model = self.__m_html_parser.on_parse_html(m_raw_html, p_request_model)
        m_leak_data_model, m_sub_url, parser_status = self.__m_html_parser.on_parse_leaks(m_raw_html, m_redirected_url)

        if not parser_status:
          m_sub_url = m_parsed_model.m_sub_url

        if helper_method.get_host_name(m_redirected_url).__eq__(helper_method.get_host_name(p_request_model.m_url)) and self.m_url_duplication_handler.validate_duplicate(m_redirected_url) is False:

          m_paresed_request_data = {"m_generic_model":json.dumps(m_parsed_model.model_dump()),  "m_leak_data_model":json.dumps(m_leak_data_model.model_dump())}
          elastic_controller.get_instance().invoke_trigger(ELASTIC_CRUD_COMMANDS.S_INDEX, [ELASTIC_REQUEST_COMMANDS.S_INDEX, json.dumps(m_paresed_request_data), ELASTIC_CONNECTIONS.S_CRAWL_INDEX])

          log.g().s(MANAGE_MESSAGES.S_LOCAL_URL_PARSED + " : " + str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + m_redirected_url)
          self.m_parsed_url.append(m_redirected_url)

          return m_parsed_model, m_sub_url
        else:
          return None, None
      else:
        log.g().w(MANAGE_MESSAGES.S_FAILED_URL_ERROR + " : " + str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " +  p_request_model.m_url + " : " + str(m_raw_html))
        return None, None
    except Exception as ex:
      log.g().e(MANAGE_MESSAGES.S_LOAD_URL_ERROR + " : " + str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + str(ex))
      return None, None

  def start_crawler_instance(self, p_request_url, p_task_id):
    p_request_url = helper_method.on_clean_url(p_request_url)
    self.__task_id = "dirlink_" + str(p_task_id)
    m_host_crawled = False
    m_failure_count = 0

    self.m_unparsed_url.append(url_model_init(p_request_url, CRAWL_SETTINGS_CONSTANTS.S_DEFAULT_DEPTH))
    while len(self.m_unparsed_url) > 0:
      item = self.m_unparsed_url.__getitem__(0)
      m_parsed_model, m_sub_url = self.__trigger_url_request(item)

      if m_parsed_model is None:
        if not m_host_crawled:
          if m_failure_count > 2:
            self.m_unparsed_url.pop(0)
          else:
            m_failure_count += 1
            sleep(5)
          continue

      if m_parsed_model is not None and item.m_depth + 1 <= CRAWL_SETTINGS_CONSTANTS.S_MAX_ALLOWED_DEPTH:
       for sub_url in m_sub_url:
         self.m_unparsed_url.append(url_model_init(sub_url, item.m_depth + 1))

      m_host_crawled = True
      self.m_unparsed_url.pop(0)

  def invoke_trigger(self, p_command, p_data=None):
    if p_command == ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE:
      self.start_crawler_instance(p_data[0], p_data[1])
    if p_command == ICRAWL_CONTROLLER_COMMANDS.S_INIT_CRAWLER_INSTANCE:
      self.init(p_data[0], p_data[1])


def genbot_instance(p_url, p_vid, p_proxy, p_tor_id):
  log.g().i(MANAGE_MESSAGES.S_PARSING_WORKER_STARTED + " : " + p_url)
  m_crawler = genbot_controller()
  m_crawler.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_INIT_CRAWLER_INSTANCE, [p_proxy, p_tor_id])
  try:
    m_crawler.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE, [p_url, p_vid])
    p_request_url = helper_method.on_clean_url(p_url)
    mongo_controller.get_instance().invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_CLOSE_INDEX_ON_COMPLETE, [p_request_url], [True]])
  except Exception as ex:
    log.g().e(MANAGE_MESSAGES.S_GENBOT_ERROR + " : " + str(p_vid) + " : " + str(ex))
  finally:
    topic_classifier_controller.get_instance().invoke_trigger(TOPIC_CLASSFIER_COMMANDS.S_CLEAN_CLASSIFIER)
    gc.collect()
    del m_crawler
