from crawler.constants.enums import network_type
from crawler.crawler_instance.proxies.i2p_controller.i2p_controller import i2p_controller
from crawler.crawler_instance.proxies.i2p_controller.i2p_enums import I2P_COMMANDS
from crawler.crawler_instance.proxies.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.proxies.tor_controller.tor_enums import TOR_COMMANDS
from crawler.crawler_services.shared.env_handler import env_handler
from crawler.crawler_services.shared.helper_method import helper_method


class shared_proxy_methods:

  @staticmethod
  def get_proxy(url):
    __m_network_type:network_type = helper_method.get_network_type(url)
    if __m_network_type == network_type.ONION or __m_network_type == network_type.CLEARNET:
      m_proxy, m_tor_id = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_PROXY, [])
    elif __m_network_type == network_type.I2P:
      m_proxy, m_tor_id = i2p_controller.get_instance().invoke_trigger(I2P_COMMANDS.S_PROXY, [])
    else:
      m_proxy, m_tor_id = None, -1
    return m_proxy, m_tor_id

  @staticmethod
  def get_onion_status():
    if env_handler.get_instance().env('ONION_ENABLED') == '1':
      return True
    else:
      return False

  @staticmethod
  def get_i2p_status():
    if env_handler.get_instance().env('I2P_ENABLED') == '1':
      return True
    else:
      return False
