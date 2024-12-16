# Local Imports

from raven.transport import requests
from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS, NETWORK_MONITOR
from crawler.constants.keys import REDIS_KEYS
from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_CONTROLLER_COMMANDS, CRAWL_MODEL_COMMANDS
from crawler.crawler_instance.crawl_controller.crawl_model import crawl_model
from crawler.crawler_services.log_manager.log_controller import log
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS
from crawler.crawler_services.request_manager.request_handler import request_handler
from crawler.crawler_services.shared.scheduler import RepeatedTimer
from crawler.shared_data import celery_shared_data


class crawl_controller(request_handler):
  # Local Variables
  __m_crawl_model = None

  # Initializations
  def __init__(self):
    self.__m_crawl_model = crawl_model()

  @staticmethod
  def __update_crawler_status():
    try:
      requests.get(CRAWL_SETTINGS_CONSTANTS.S_UPDATE_STATUS_URL, timeout=100)
    except Exception:
      pass

  @staticmethod
  def __update_internet_status():
    url = NETWORK_MONITOR.S_PING_URL
    timeout = 5
    try:
      requests.head(url, timeout=timeout)
      celery_shared_data.get_instance().set_network_status(True)
    except Exception:
      celery_shared_data.get_instance().set_network_status(False)
      log.g().w(MANAGE_MESSAGES.S_INTERNET_CONNECTION_ISSUE)

  def __on_start(self):
    if APP_STATUS.DOCKERIZED_RUN:
      RepeatedTimer(CRAWL_SETTINGS_CONSTANTS.S_UPDATE_STATUS_TIMEOUT, self.__update_crawler_status)
      RepeatedTimer(CRAWL_SETTINGS_CONSTANTS.S_UPDATE_NETWORK_STATUS_TIMEOUT, self.__update_internet_status)
      redis_controller().invoke_trigger(REDIS_COMMANDS.S_SET_BOOL, [REDIS_KEYS.S_NETWORK_MONITOR_STATUS, True, None])
    else:
      celery_shared_data.get_instance().set_network_status(True)

    self.__m_crawl_model.invoke_trigger(CRAWL_MODEL_COMMANDS.S_INIT)

  def invoke_trigger(self, p_command, p_data=None):
    if p_command == CRAWL_CONTROLLER_COMMANDS.S_RUN_CRAWLER:
      self.__on_start()
