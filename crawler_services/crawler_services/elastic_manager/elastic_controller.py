# Local Imports
from elasticsearch import Elasticsearch

from crawler_services.constants.strings import MANAGE_ELASTIC_MESSAGES
from crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CRUD_COMMANDS, ELASTIC_KEYS, ELASTIC_INDEX, ELASTIC_CONNECTIONS
from crawler_services.crawler_services.elastic_manager.elastic_request_generator import elastic_request_generator
from crawler_shared_directory.log_manager.log_controller import log
from crawler_shared_directory.request_manager.request_handler import request_handler


class elastic_controller(request_handler):
    __instance = None
    __m_connection = None
    __m_elastic_request_generator = None

    # Initializations
    @staticmethod
    def get_instance():
        if elastic_controller.__instance is None:
            elastic_controller()
        return elastic_controller.__instance

    def __init__(self):
        elastic_controller.__instance = self
        self.__m_elastic_request_generator = elastic_request_generator()
        self.__link_connection()

    def __link_connection(self):
        self.__m_connection = Elasticsearch(ELASTIC_CONNECTIONS.S_DATABASE_IP + ":" + str(ELASTIC_CONNECTIONS.S_DATABASE_PORT))
        self.__initialization()

    def __initialization(self):
        try:
            # self.__m_connection.indices.delete(index=ELASTIC_INDEX.S_WEB_INDEX, ignore=[400, 404])

            settings = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                },
                "mappings": {
                    "properties": {
                        'm_host': {
                            "index": "not_analyzed",
                            'type': 'keyword'
                        },
                        'm_subhost': {
                            'type': 'keyword',
                            "index": "not_analyzed"
                        },
                        "m_doc_size": {'type': 'integer'},
                        "m_img_size": {'type': 'integer'},
                        'p_title': {'type': 'string'},
                        'm_meta_description': {'type': 'string'},
                        'm_meta_keywords': {'type': 'string'},
                        'm_content': {'type': 'string'},
                        'm_content_type': {'type': 'keyword'},
                        'm_sub_url': {},
                        'm_images': {},
                        'm_video': {},
                        'm_doc_url': {},
                        'm_date': {'type': 'date'},
                    }
                }
            }
            self.__m_connection.index(index=ELASTIC_INDEX.S_WEB_INDEX, id=1, body=settings)
            pass

        except Exception as ex:
            log.g().e("ELASTIC 1 : " + MANAGE_ELASTIC_MESSAGES.S_INSERT_FAILURE + " : " + str(ex))


    def __update(self, p_data, p_upsert):
        try:
            self.__m_connection.index(body=p_data[ELASTIC_KEYS.S_VALUE], index=p_data[ELASTIC_KEYS.S_DOCUMENT])
        except Exception as ex:
            log.g().e("ELASTIC 2 : " + MANAGE_ELASTIC_MESSAGES.S_INSERT_FAILURE + " : " + str(ex))
            return False, str(ex)

    def __read(self, p_data):
        try:
            m_json = self.__m_connection.search(index=p_data[ELASTIC_KEYS.S_DOCUMENT], body=p_data[ELASTIC_KEYS.S_FILTER])
            return m_json['hits']['hits']
        except Exception as ex:
            log.g().e("ELASTIC 3 : " + MANAGE_ELASTIC_MESSAGES.S_INSERT_FAILURE + " : " + str(ex))
            return False, str(ex)

    def invoke_trigger(self, p_commands, p_data=None):
        m_request = p_data[0]
        m_data = p_data[1]
        m_param = p_data[2]

        m_request = self.__m_elastic_request_generator.invoke_trigger(m_request, m_data)
        if p_commands == ELASTIC_CRUD_COMMANDS.S_UPDATE:
            return self.__update(m_request, m_param[0])
        if p_commands == ELASTIC_CRUD_COMMANDS.S_READ:
            return self.__read(m_request)
