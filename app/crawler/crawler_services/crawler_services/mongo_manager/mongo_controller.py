# Local Imports
import pymongo

from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CRUD, MONGODB_KEYS, MONGO_CONNECTIONS, MONGODB_PROPERTIES
from crawler.crawler_services.crawler_services.mongo_manager.mongo_request_generator import mongo_request_generator
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class mongo_controller(request_handler):
  __m_connection = None
  __m_mongo_request_generator = None

  def __init__(self):
    self.__m_mongo_request_generator = mongo_request_generator()
    self.__link_connection()

  def close_connection(self):
    self.__m_connection.client.close()

  def __del__(self):
    self.close_connection()

  @classmethod
  def destroy_instance(cls):
      cls.__instance = None

  def __link_connection(self):
    connection_params = {
      'host': MONGO_CONNECTIONS.S_MONGO_IP,
      'port': MONGO_CONNECTIONS.S_MONGO_PORT,
    }

    auth_params = {
      'username': MONGO_CONNECTIONS.S_MONGO_USERNAME,
      'password': MONGO_CONNECTIONS.S_MONGO_PASSWORD
    }

    connection_params.update({k: v for k, v in auth_params.items() if v})
    self.__m_connection = pymongo.MongoClient(MONGO_CONNECTIONS.S_MONGO_IP, MONGO_CONNECTIONS.S_MONGO_PORT, username=MONGO_CONNECTIONS.S_MONGO_USERNAME, password=MONGO_CONNECTIONS.S_MONGO_PASSWORD, maxPoolSize=10)[MONGO_CONNECTIONS.S_MONGO_DB_NAME]

  def __reset(self, p_data):
    try:
      self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].update_many(p_data[MONGODB_KEYS.S_FILTER], p_data[MONGODB_KEYS.S_VALUE])
      return True, MANAGE_MESSAGES.S_UPDATE_SUCCESS

    except Exception as ex:
      log.g().e(MANAGE_MESSAGES.S_UPDATE_FAILURE + " : " + str(ex))
      return False, str(ex)

  def __create(self, p_data):
    try:
      self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].insert(p_data[MONGODB_KEYS.S_VALUE])
      return True, MANAGE_MESSAGES.S_INSERT_SUCCESS
    except Exception as ex:
      log.g().e(MANAGE_MESSAGES.S_INSERT_FAILURE + " : " + str(ex))
      return False, str(ex)

  def __read(self, p_data):
    try:
      documents = self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].find(p_data[MONGODB_KEYS.S_FILTER], p_data[MONGODB_KEYS.S_VALUE])
      if MONGODB_PROPERTIES.S_SORT in p_data:
        m_sort_query = p_data[MONGODB_PROPERTIES.S_SORT]
        documents.sort(m_sort_query[0], m_sort_query[1])

      return documents
    except Exception as ex:
      log.g().e(MANAGE_MESSAGES.S_READ_FAILURE + " : " + str(ex))
      return str(ex)

  def __update(self, p_data, upsert=True):
    try:
      self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].update_many(p_data[MONGODB_KEYS.S_FILTER], p_data[MONGODB_KEYS.S_VALUE], upsert=upsert)
      return True, MANAGE_MESSAGES.S_UPDATE_SUCCESS

    except Exception as ex:
      log.g().e(MANAGE_MESSAGES.S_UPDATE_FAILURE + " : " + str(ex))
      return False, str(ex)

  def __delete(self, p_data):
    try:
      self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].delete_many(p_data[MONGODB_KEYS.S_FILTER])
      return True, MANAGE_MESSAGES.S_DELETE_SUCCESS
    except Exception as ex:
      log.g().e(MANAGE_MESSAGES.S_DELETE_FAILURE + " : " + str(ex))
      return False, str(ex)

  def invoke_trigger(self, p_commands, p_data=None):

    m_request = p_data[0]
    m_data = p_data[1]
    m_param = p_data[2]

    m_request = self.__m_mongo_request_generator.invoke_trigger(m_request, m_data)

    if p_commands == MONGO_CRUD.S_CREATE:
      return self.__create(m_request)
    elif p_commands == MONGO_CRUD.S_READ:
      return self.__read(m_request)
    elif p_commands == MONGO_CRUD.S_UPDATE:
      return self.__update(m_request, m_param[0])
    elif p_commands == MONGO_CRUD.S_DELETE:
      return self.__delete(m_request)
    elif p_commands == MONGO_CRUD.S_RESET:
      return self.__reset(m_request)
