import enum

class MONGODB_COMMANDS(enum.Enum):
    S_RESET = -1
    S_SAVE_BACKUP = 1
    S_INSTALL_CRAWLABLE_URL = 9
    S_CLEAR_CRAWLABLE_URL_DATA = 10
    S_GET_CRAWLABLE_URL_DATA = 11
    S_UPDATE_CRAWLABLE_URL_DATA = 12
    S_RESET_CRAWLABLE_URL = 14
    S_CLEAR_BACKUP = 16
    S_CLEAR_UNIQUE_HOST = 18
    S_REMOVE_BACKUP = 19
    S_GET_UNPARSED_URL = 20
    S_SET_BACKUP_URL = 21
    S_COUNT_CRAWLED_URL = 23

class MONGODB_COLLECTIONS:
    S_BACKUP_MODEL = 'backup_model'
    S_CRAWLABLE_URL_MODEL = 'crawlable_url_model'

class MONGO_CONNECTIONS:
    S_DATABASE_NAME = 'genesis-search'
    S_DATABASE_PORT = 27017
    S_DATABASE_IP = 'localhost'

class MONGO_CRUD(enum.Enum):
    S_CREATE = '1'
    S_READ = '2'
    S_UPDATE = '3'
    S_DELETE = '4'
    S_CREATE_UNIQUE = '5'
    S_COUNT = '6'

class MONGODB_KEYS:
    S_DOCUMENT = 'm_document'
    S_FILTER = 'm_filter'
    S_VALUE = 'm_value'
