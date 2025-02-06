# Local Imports
import gc
from asyncio import sleep
from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_instance.genbot_service.custom_parse_controller import custom_parse_controller
from crawler.crawler_instance.genbot_service.generic_parse_controller import generic_parse_controller
from crawler.crawler_services.mongo_manager.mongo_controller import mongo_controller
from crawler.crawler_services.mongo_manager.mongo_enums import MONGO_CRUD, MONGODB_COMMANDS
from crawler.crawler_services.request_manager.request_handler import request_handler
from crawler.crawler_instance.genbot_service.genbot_enums import ICRAWL_CONTROLLER_COMMANDS
from crawler.crawler_services.shared.helper_method import helper_method
from crawler.crawler_services.log_manager.log_controller import log


class genbot_controller(request_handler):

  def __init__(self):

    self.__generic_parse_controller = generic_parse_controller()
    self.__custom_parse_controller = custom_parse_controller()


  def init(self, p_proxy, p_tor_id):
    self.__generic_parse_controller.init(p_proxy, p_tor_id)
    self.__custom_parse_controller.init(p_proxy, p_tor_id)

  def start_crawler_instance(self, p_request_url, _):
    try:
      self.__custom_parse_controller.on_init_leak_parser(p_request_url)
      if self.__custom_parse_controller.leak_extractor_instance is not None:
        generic_parse_mapping = self.__custom_parse_controller.on_leak_parser_invoke()
        self.__generic_parse_controller.start_custom_crawler_instance(generic_parse_mapping)
      else:
        self.__generic_parse_controller.start_crawler_instance(p_request_url)
    finally:
      self.__generic_parse_controller.on_clear()

  def invoke_trigger(self, p_command, p_data=None):
    if p_command == ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE:
      self.start_crawler_instance(p_data[0], p_data[1])
    if p_command == ICRAWL_CONTROLLER_COMMANDS.S_INIT_CRAWLER_INSTANCE:
      self.init(p_data[0], p_data[1])


def genbot_instance(p_url, p_vid, p_proxy, p_tor_id):
  p_url = "http://weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd.onion"
  log.g().i(MANAGE_MESSAGES.S_PARSING_WORKER_STARTED + " : " + p_url)
  m_crawler = genbot_controller()
  m_crawler.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_INIT_CRAWLER_INSTANCE, [p_proxy, p_tor_id])
  mongo = mongo_controller()
  try:
    m_crawler.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE, [p_url, p_vid])
    p_request_url = helper_method.on_clean_url(p_url)
    mongo.invoke_trigger(MONGO_CRUD.S_UPDATE, [MONGODB_COMMANDS.S_CLOSE_INDEX_ON_COMPLETE, [p_request_url], [True]])
  except Exception as ex:
    log.g().e(MANAGE_MESSAGES.S_GENBOT_ERROR + " : " + p_url + " : " + str(p_vid) + " : " + str(ex))
  finally:
    mongo.close_connection()
    del m_crawler
    gc.collect()
    sleep(5)
