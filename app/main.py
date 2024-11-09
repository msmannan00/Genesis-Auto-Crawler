from crawler.crawler_instance.genbot_service.shared_data_controller import shared_data_controller
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.constants.strings import TOR_STRINGS, MANAGE_MESSAGES
log.g().i(MANAGE_MESSAGES.S_INCLUDES_STARTING)

import argparse
from crawler.constants.app_status import APP_STATUS
from crawler.constants.constant import RAW_PATH_CONSTANTS, CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_instance.application_controller.application_controller import application_controller
from crawler.crawler_instance.application_controller.application_enums import APPICATION_COMMANDS
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CONNECTIONS
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CONNECTIONS
from crawler.crawler_services.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.crawler_services.redis_manager.redis_enums import REDIS_CONNECTIONS, REDIS_KEYS, REDIS_COMMANDS
from pathlib import Path

def initialize_local_setting():
  APP_STATUS.DOCKERIZED_RUN = False
  RAW_PATH_CONSTANTS.TOXIC_MODEL = str(Path(__file__).parent.parent) + "/app/raw/toxic_model/"

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
  ELASTIC_CONNECTIONS.S_CRAWL_UNIQUE_INDEX = "http://localhost:8080/feeder/publish"

  CRAWL_SETTINGS_CONSTANTS.S_FEEDER_URL = "http://localhost:8080/feeder"
  CRAWL_SETTINGS_CONSTANTS.S_PARSERS_URL = "http://localhost:8080/parser"
  CRAWL_SETTINGS_CONSTANTS.S_PARSERS_URL_UNIQUE = "http://localhost:8080/parser/unique"
  CRAWL_SETTINGS_CONSTANTS.S_FEEDER_URL_UNIQUE = "http://localhost:8080/feeder/unique"
  shared_data_controller.get_instance().init()


def main():
  default_command = 'local_run'
  parser = argparse.ArgumentParser(description='Crawler application initializer')
  parser.add_argument('--command', type=str, default=default_command)

  args = parser.parse_args()

  try:

    if args.command == 'local_run':
      initialize_local_setting()
      application_controller.get_instance().invoke_triggers(APPICATION_COMMANDS.S_START_APPLICATION_DIRECT)

    elif args.command == 'local_unique_crawler_run':
      from crawler.crawler_instance.genbot_service.genbot_unique_controller import genbot_unique_instance
      from crawler.crawler_instance.genbot_service.genbot_unique_controller import prepare_and_fetch_data

      initialize_local_setting()
      redis_controller().invoke_trigger(REDIS_COMMANDS.S_SET_BOOL, [REDIS_KEYS.UNIQIE_CRAWLER_RUNNING, False, None])
      content_list = prepare_and_fetch_data(CRAWL_SETTINGS_CONSTANTS.S_FEEDER_URL)
      m_proxy, m_tor_id = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_PROXY, [])
      genbot_unique_instance(content_list, m_proxy, m_tor_id)

    elif args.command == 'invoke_celery_crawler':
      from crawler.crawler_services.crawler_services.celery_manager.celery_controller import celery_controller
      from crawler.crawler_services.crawler_services.celery_manager.celery_enums import CELERY_COMMANDS

      redis_controller().invoke_trigger(REDIS_COMMANDS.S_SET_BOOL, [REDIS_KEYS.UNIQIE_CRAWLER_RUNNING, False, None])
      APP_STATUS.DOCKERIZED_RUN = True
      application_controller.get_instance().invoke_triggers(APPICATION_COMMANDS.S_START_APPLICATION_DOCKERISED)

    elif args.command == 'invoke_unique_crawler':
      from crawler.crawler_services.crawler_services.celery_manager.celery_controller import celery_controller
      from crawler.crawler_services.crawler_services.celery_manager.celery_enums import CELERY_COMMANDS
      from crawler.crawler_instance.genbot_service.genbot_unique_controller import prepare_and_fetch_data

      content_list = prepare_and_fetch_data(CRAWL_SETTINGS_CONSTANTS.S_FEEDER_URL)
      celery_controller.get_instance().invoke_trigger(CELERY_COMMANDS.S_INVOKE_UNIQUE_CRAWLER, content_list)

  except Exception as ex:
    log.g().e(MANAGE_MESSAGES.S_APPLICATION_ERROR + " : " + str(ex))


if __name__ == "__main__":
  main()
