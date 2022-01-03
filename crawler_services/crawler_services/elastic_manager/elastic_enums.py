class ELASTIC_CRUD_COMMANDS:
    S_CREATE = 1
    S_READ = 2
    S_UPDATE = 3
    S_DELETE = 4

class ELASTIC_INDEX:
    S_WEB_INDEX = "parsed_index"

class ELASTIC_CONNECTIONS:
    S_DATABASE_NAME = 'genesis-elastic_manager-search'
    S_DATABASE_PORT = 9200
    S_DATABASE_IP = 'http://localhost'

class ELASTIC_KEYS:
    S_DOCUMENT = 'm_document'
    S_FILTER = 'm_filter'
    S_VALUE = 'm_value'

class ELASTIC_REQUEST_COMMANDS:
    S_SEARCH = 1
    S_INDEX = 2
    S_UNIQUE_HOST = 3
    S_DUPLICATE = 4
