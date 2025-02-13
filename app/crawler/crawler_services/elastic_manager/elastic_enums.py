from crawler.crawler_services.shared.env_handler import env_handler
S_SERVER = env_handler.get_instance().env('S_SERVER', 'http://localhost:8080')

class ELASTIC_CRUD_COMMANDS:
  S_INDEX = 7

class ELASTIC_REQUEST_COMMANDS:
  S_INDEX = 7
  S_UNIQUE_INDEX = 8

class ELASTIC_CONNECTIONS:
  S_INDEX_LEAK = f"{S_SERVER}/api/index/leak"
  S_INDEX_GENERIC = f"{S_SERVER}/api/index/generic"
