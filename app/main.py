from crawler.crawler_instance.genbot_service.shared_data_controller import shared_data_controller
from crawler.crawler_instance.proxies.i2p_controller.i2p_controller import i2p_controller
from crawler.crawler_instance.proxies.i2p_controller.i2p_enums import I2P_PROXY, I2P_COMMANDS
from crawler.crawler_services.log_manager.log_controller import log
from crawler.constants.strings import TOR_STRINGS, MANAGE_MESSAGES
from crawler.crawler_services.mongo_manager.mongo_enums import MONGO_CONNECTIONS
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_CONNECTIONS, REDIS_COMMANDS, REDIS_KEYS

log.g().i(MANAGE_MESSAGES.S_INCLUDES_STARTING)

import argparse
from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import RAW_PATH_CONSTANTS, CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_instance.application_controller.application_controller import application_controller
from crawler.crawler_instance.application_controller.application_enums import APPICATION_COMMANDS
from crawler.crawler_services.elastic_manager.elastic_enums import ELASTIC_CONNECTIONS
from pathlib import Path

def initialize_local_setting():
  APP_STATUS.DOCKERIZED_RUN = False
  RAW_PATH_CONSTANTS.MODEL = str(Path(__file__).parent.parent) + "/app/raw/model/"

  MONGO_CONNECTIONS.S_MONGO_IP = "localhost"
  MONGO_CONNECTIONS.S_MONGO_USERNAME = ""
  MONGO_CONNECTIONS.S_MONGO_PASSWORD = ""
  MONGO_CONNECTIONS.S_MONGO_PORT = 27017

  TOR_STRINGS.S_SOCKS_HTTPS_PROXY = "socks5h://127.0.0.1:"
  TOR_STRINGS.S_SOCKS_HTTP_PROXY = "socks5h://127.0.0.1:"

  REDIS_CONNECTIONS.S_DATABASE_IP = "localhost"
  REDIS_CONNECTIONS.S_DATABASE_PASSWORD = ""

  RAW_PATH_CONSTANTS.LOG_DIRECTORY = "logs"

  ELASTIC_CONNECTIONS.S_CRAWL_INDEX = "http://localhost:8080/crawl_index/"

  CRAWL_SETTINGS_CONSTANTS.S_FEEDER_URL = "http://localhost:8080/feeder"
  CRAWL_SETTINGS_CONSTANTS.S_PARSERS_URL = "http://localhost:8080/parser"
  CRAWL_SETTINGS_CONSTANTS.S_PARSERS_URL_UNIQUE = "http://localhost:8080/parser/unique"
  CRAWL_SETTINGS_CONSTANTS.S_FEEDER_URL_UNIQUE = "http://localhost:8080/feeder/unique"
  CRAWL_SETTINGS_CONSTANTS.S_SEARCH_SERVER = "http://localhost:8080"
  shared_data_controller.get_instance().init()
  I2P_PROXY.PROXY_URL_HTTP = "http://127.0.0.1:4444"
  I2P_PROXY.PROXY_URL_HTTPS = "http://127.0.0.1:7654"

def main():
  default_command = 'local_run'
  parser = argparse.ArgumentParser(description='Crawler application initializer')
  parser.add_argument('--command', type=str, default=default_command)

  args = parser.parse_args()

  try:

    if args.command == 'local_run':
      initialize_local_setting()
      application_controller.get_instance().invoke_trigger(APPICATION_COMMANDS.S_START_APPLICATION_DIRECT)

    elif args.command == 'invoke_celery_crawler':
      redis_controller().invoke_trigger(REDIS_COMMANDS.S_SET_BOOL, [REDIS_KEYS.UNIQIE_CRAWLER_RUNNING, False, None])
      APP_STATUS.DOCKERIZED_RUN = True
      application_controller.get_instance().invoke_trigger(APPICATION_COMMANDS.S_START_APPLICATION_DOCKERISED)

  except Exception as ex:
    log.g().e(MANAGE_MESSAGES.S_APPLICATION_ERROR + " : TRACEBACK : " + str(ex.__traceback__))


if __name__ == "__main__":
  main()
