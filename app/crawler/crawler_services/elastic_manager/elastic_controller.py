# Local Imports
from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_services.shared.web_request_handler import webRequestManager
from crawler.crawler_services.log_manager.log_controller import log
from crawler.crawler_services.request_manager.request_handler import request_handler


class elastic_controller(request_handler):
  @classmethod
  def destroy_instance(cls):
      cls.__instance = None

  @staticmethod
  def __post_data(p_data):
    web_request_manager = webRequestManager()
    m_counter = 0
    while True:
      try:
        m_post_object = p_data[1]
        url = p_data[2]

        m_response, status_code = web_request_manager.request_server_post(url, data=m_post_object)

        if status_code != 200:
          log.g().e(MANAGE_MESSAGES.S_ELASTIC_ERROR + " : HTTP Status Code " + str(status_code))
          return False
        return True

      except Exception as ex:
        m_counter += 1
        log.g().e(MANAGE_MESSAGES.S_ELASTIC_ERROR + " : " + str(ex))
        if m_counter > 5:
          return False, None

  def invoke_trigger(self, p_commands, p_data=None):
    return self.__post_data(p_data)
