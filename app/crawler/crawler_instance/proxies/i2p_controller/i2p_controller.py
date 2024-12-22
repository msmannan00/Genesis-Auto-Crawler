from time import sleep

import requests

from crawler.crawler_instance.proxies.i2p_controller.i2p_enums import I2P_PROXY, I2P_COMMANDS
from crawler.crawler_services.log_manager.log_controller import log
from crawler.crawler_services.request_manager.request_handler import request_handler


class i2p_controller(request_handler):
  __instance = None

  @staticmethod
  def get_instance():
    if i2p_controller.__instance is None:
      i2p_controller.__instance = i2p_controller()
    return i2p_controller.__instance

  def __init__(self):
    if i2p_controller.__instance is not None:
      raise Exception("This is a singleton class. Use get_instance() to get the instance.")
    self.m_request_index = 0

  @staticmethod
  def fetch_known_urls():
    urls = []
    while len(urls) == 0:
      urls = []
      proxies = {'http': I2P_PROXY.PROXY_URL_HTTP, 'https': I2P_PROXY.PROXY_URL_HTTPS}

      for subscription_url in I2P_PROXY.SUBSCRIPTION_URLS:
        try:
          response = requests.get(subscription_url, proxies=proxies)
          response.raise_for_status()

          for line in response.text.splitlines():
            if line.strip() and not line.startswith('#'):
              url = line.split('=')[0].strip()

              if not url.startswith('http'):
                url = f'http://{url}'

              urls.append(url)
        except requests.exceptions.RequestException as e:
          log.g().e("I2P Error fetching from " + str(e))
      if len(urls) == 0:
        sleep(10)

    log.g().i(urls)
    return urls

  @staticmethod
  def get_proxy():
    return {'http': I2P_PROXY.PROXY_URL_HTTP, 'https': I2P_PROXY.PROXY_URL_HTTPS}, -1

  def invoke_trigger(self, p_command, p_data=None):
    if p_command == I2P_COMMANDS.S_FETCH:
      return self.fetch_known_urls()
    if p_command == I2P_COMMANDS.S_PROXY:
      return self.get_proxy()
