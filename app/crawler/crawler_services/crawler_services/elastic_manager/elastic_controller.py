# Local Imports
import json

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from crawler.constants.strings import MANAGE_ELASTIC_MESSAGES, MANAGE_CRAWLER_MESSAGES
from crawler.crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CONNECTIONS
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class elastic_controller(request_handler):
    __instance = None

    # Initializations
    @staticmethod
    def get_instance():
        if elastic_controller.__instance is None:
            elastic_controller()
        return elastic_controller.__instance

    def __init__(self):
        elastic_controller.__instance = self

    def __post_data(self, p_commands, p_data):
        m_counter = 0
        while True:
            try:
                m_json_data = json.dumps(p_data)
                m_post_object = {'pRequestCommand': p_commands, "pRequestData": m_json_data}
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                m_response = session.post(ELASTIC_CONNECTIONS.S_DATABASE_IP, data=m_post_object)
                m_data = json.loads(m_response.text)
                m_status = m_data[0]
                m_data = m_data[1]
                if not m_status:
                    log.g().e(MANAGE_ELASTIC_MESSAGES.S_REQUEST_FAILURE + " : " + str(m_data))
                elif m_data:
                    log.g().s(MANAGE_ELASTIC_MESSAGES.S_REQUEST_SUCCESS + " : " + str(m_data))
                    m_data = m_data['hits']['hits']
                return m_status, m_data
            except Exception as ex:
                m_counter+=1
                log.g().e(MANAGE_CRAWLER_MESSAGES.S_ELASTIC_ERROR + " : " + str(ex))
                if m_counter>5:
                    return False, None

    def invoke_trigger(self, p_commands, p_data=None):
        return self.__post_data(p_commands, p_data)
