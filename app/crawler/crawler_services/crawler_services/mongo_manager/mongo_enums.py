import enum
from crawler.crawler_services.helper_services.env_handler import env_handler

class MONGODB_COMMANDS(enum.Enum):
  S_INSTALL_CRAWLABLE_URL = 1
  S_GET_CRAWLABLE_URL_DATA = 2
  S_REMOVE_DEAD_CRAWLABLE_URL = 3
  S_CLOSE_INDEX_ON_COMPLETE = 4
  S_UPDATE_INDEX = 5
  S_GET_INDEX = 6
  S_RESET_CRAWLABLE_URL = 7
  S_SET_CRAWLABLE_URL = 8


class MONGODB_COLLECTIONS:
  S_MONGO_INDEX_MODEL = 'index_model'


class MONGO_CONNECTIONS:
  S_MONGO_DB_NAME = "trustly-crawler"
  S_MONGO_USERNAME = env_handler.get_instance().env('MONGO_ROOT_USERNAME')
  S_MONGO_PASSWORD = env_handler.get_instance().env('MONGO_ROOT_PASSWORD')
  S_MONGO_PORT = 27017
  S_MONGO_IP = 'mongo'


class MONGO_CRUD(enum.Enum):
  S_CREATE = '1'
  S_READ = '2'
  S_UPDATE = '3'
  S_DELETE = '4'
  S_RESET = '5'
  S_COUNT = '6'
  S_UPDATE_BULK = '7'


class MONGODB_KEYS:
  S_DOCUMENT = 'm_document'
  S_FILTER = 'm_filter'
  S_VALUE = 'm_value'


class MONGODB_PROPERTIES:
  S_SORT = 'm_sort'
