# Local Imports
import pymongo

from pymongo import WriteConcern
from crawler_instance.log_manager.log_controller import log
from crawler_services.constants.constant import mongo_constants
from crawler_services.crawler_services.mongo_manager.mongo_enums import MONGO_CRUD, MANAGE_USER_MESSAGES, MONGODB_KEYS
from crawler_services.crawler_services.mongo_manager.mongo_request_generator import mongo_request_generator
from crawler_services.shared_model.request_handler import request_handler


class mongo_controller(request_handler):
    __instance = None
    __m_connection = None
    __m_mongo_request_generator = None

    # Initializations
    @staticmethod
    def get_instance():
        if mongo_controller.__instance is None:
            mongo_controller()
        return mongo_controller.__instance

    def __init__(self):
        mongo_controller.__instance = self
        self.__m_mongo_request_generator = mongo_request_generator()
        self.__link_connection()

    def __link_connection(self):
        self.__m_connection = pymongo.MongoClient(mongo_constants.S_DATABASE_IP, mongo_constants.S_DATABASE_PORT)[mongo_constants.S_DATABASE_NAME]

    def __create_unique(self, p_data):
        try:
            self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].with_options(write_concern=WriteConcern(w=0)).insert(p_data[MONGODB_KEYS.S_VALUE])

            return True, MANAGE_USER_MESSAGES.S_INSERT_SUCCESS
        except Exception as ex:
            log.g().e("E8 : " + MANAGE_USER_MESSAGES.S_INSERT_FAILURE + " : " + str(ex))
            return False, str(ex)

    def __create(self, p_data):
        try:
            self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].insert(p_data[MONGODB_KEYS.S_VALUE])
            return True, MANAGE_USER_MESSAGES.S_INSERT_SUCCESS
        except Exception as ex:
            log.g().e("E9 : " + MANAGE_USER_MESSAGES.S_INSERT_FAILURE + " : " + str(ex))
            return False, str(ex)

    def __read(self, p_data, p_limit):
        try:
            if p_limit is not None:
                documents = self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].find(p_data[MONGODB_KEYS.S_FILTER]).limit(p_limit)
            else:
                documents = self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].find(p_data[MONGODB_KEYS.S_FILTER])
            return documents
        except Exception as ex:
            log.g().e("E10 : " + MANAGE_USER_MESSAGES.S_READ_FAILURE)
            return str(ex)

    def __update(self, p_data):
        try:
            self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].update_many(p_data[MONGODB_KEYS.S_FILTER],p_data[MONGODB_KEYS.S_VALUE], upsert=True)
            return True, MANAGE_USER_MESSAGES.S_UPDATE_SUCCESS

        except Exception as ex:
            log.g().e("E11 : " + MANAGE_USER_MESSAGES.S_UPDATE_FAILURE)
            return False, str(ex)

    def __delete(self, p_data):
        try:
            documents = self.__m_connection[p_data[MONGODB_KEYS.S_DOCUMENT]].remove(p_data[MONGODB_KEYS.S_FILTER])
            return documents, MANAGE_USER_MESSAGES.S_DELETE_SUCCESS
        except Exception as ex:
            log.g().e("E12 : " + MANAGE_USER_MESSAGES.S_DELETE_FAILURE)
            return False, str(ex)

    def invoke_trigger(self, p_commands, p_data=None):
        m_request = self.__m_mongo_request_generator.invoke_trigger(p_data[0], p_data[1:])
        if p_commands == MONGO_CRUD.S_CREATE:
            return self.__create(m_request)
        elif p_commands == MONGO_CRUD.S_READ:
            return self.__read(m_request, p_data[1])
        elif p_commands == MONGO_CRUD.S_UPDATE:
            return self.__update(m_request)
        elif p_commands == MONGO_CRUD.S_DELETE:
            return self.__delete(m_request)
        elif p_commands == MONGO_CRUD.S_CREATE_UNIQUE:
            return self.__create_unique(m_request)
