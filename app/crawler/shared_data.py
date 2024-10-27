from crawler.constants.keys import REDIS_KEYS
from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_services.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS


class celery_shared_data:
  __m_running = False
  __instance = None

  # Initializations
  @staticmethod
  def get_instance():
    if celery_shared_data.__instance is None:
      celery_shared_data()
    return celery_shared_data.__instance

  def __init__(self):
    if celery_shared_data.__instance is not None:
      raise Exception(MANAGE_MESSAGES.S_SINGLETON_EXCEPTION)
    else:
      celery_shared_data.__instance = self
    self.redis_controller_instance = redis_controller()

  def get_network_status(self):
    return self.redis_controller_instance.invoke_trigger(REDIS_COMMANDS.S_GET_BOOL, [REDIS_KEYS.S_NETWORK_MONITOR_STATUS, False, None])

  def set_network_status(self, p_status):
    self.redis_controller_instance.invoke_trigger(REDIS_COMMANDS.S_SET_BOOL, [REDIS_KEYS.S_NETWORK_MONITOR_STATUS, p_status, None])
