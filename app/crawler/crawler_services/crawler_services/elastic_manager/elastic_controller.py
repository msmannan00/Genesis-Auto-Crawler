# Local Imports
from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CONNECTIONS, \
  ELASTIC_REQUEST_COMMANDS, ELASTIC_CRUD_COMMANDS
from crawler.crawler_services.web_request_handler import webRequestManager
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class elastic_controller(request_handler):
  __instance = None

  @staticmethod
  def get_instance():
    if elastic_controller.__instance is None:
      elastic_controller()
    return elastic_controller.__instance

  def __init__(self):
    if elastic_controller.__instance is not None:
      raise Exception("This class is a singleton!")
    else:
      elastic_controller.__instance = self

  @classmethod
  def destroy_instance(cls):
      cls.__instance = None

  def __post_data(self, p_data, unique_index=False):
    web_request_manager = webRequestManager()
    m_counter = 0
    while True:
      try:
        m_post_object = {'pRequestCommand': p_data[0], 'pRequestData': p_data[1]}
        url = p_data[2]

        m_response, status_code = web_request_manager.request_server_post(url, data=m_post_object)

        if status_code != 200:
          log.g().e(MANAGE_MESSAGES.S_ELASTIC_ERROR + " : HTTP Status Code " + str(status_code))
          return False, None

        m_status = m_response[0]
        m_data = m_response[1]

        if not m_status:
          log.g().e(MANAGE_MESSAGES.S_REQUEST_FAILURE + " : " + str(m_data))
        elif m_data and not unique_index:
          log.g().s(MANAGE_MESSAGES.S_REQUEST_SUCCESS + " : " + str(m_data))
          m_data = m_data['hits']['hits']
        return m_status, m_data

      except Exception as ex:
        m_counter += 1
        log.g().e(MANAGE_MESSAGES.S_ELASTIC_ERROR + " : " + str(ex))
        if m_counter > 5:
          return False, None

  def invoke_trigger(self, p_commands, p_data=None):
    return self.__post_data(p_data, p_commands == ELASTIC_CRUD_COMMANDS.S_INDEX)
