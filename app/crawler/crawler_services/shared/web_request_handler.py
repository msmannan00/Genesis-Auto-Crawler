from raven.transport import requests
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_services.log_manager.log_controller import log
from crawler.crawler_services.shared.crypto_handler import crypto_handler
from crawler.crawler_services.shared.helper_method import helper_method


class webRequestManager:

  def __init__(self):
    pass

  def fetch(self, p_url, p_proxy, headers):
    try:
      proxy_url = next(iter(p_proxy.values()))
      ip_port = proxy_url.split('//')[1]
      ip, port = ip_port.split(':')
      proxy_host = p_proxy.get('host', ip)
      proxy_port = p_proxy.get('port', port)

      proxies = {
        "http": f"socks5h://{proxy_host}:{proxy_port}",
        "https": f"socks5h://{proxy_host}:{proxy_port}"
      }

      response = requests.get(p_url, headers=headers, proxies=proxies, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT)
      response.raise_for_status()
      return response.text, response.status_code, response.url

    except Exception as ex:
      return str(ex), None, None

  def load_url(self, p_url, p_custom_proxy):
    try:
      headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Cache-Control': 'no-cache'
      }

      m_html, m_status, m_url_redirect = self.fetch(p_url, p_custom_proxy, headers)
      if m_html == "" or m_status != 200:
        return str(p_url), False, m_status
      else:
        return helper_method.on_clean_url(str(m_url_redirect)), True, str(m_html)
    except Exception as ex:
      log.g().e(MANAGE_MESSAGES.S_LOAD_URL_ERROR_MAIN + " : " + str(ex))
      return p_url, False, None

  def request_server_post(self, url, data=None, params=None, timeout=1000):
    response = None
    try:
      crypto = crypto_handler()
      secret_token = crypto.generate_secret_token()

      headers = {
        'pSecretToken': f'{secret_token}',
        'Content-Type': 'application/json'
      }

      response = requests.post(url, json=data, params=params, headers=headers, timeout=timeout)
      response.raise_for_status()
      return response.json(), response.status_code

    except Exception as ex:
      return None, str(ex)

    finally:
      if response is not None:
        response.close()

  def request_server_get(self, url, params=None, timeout=1000):
    try:
      crypto = crypto_handler()
      secret_token = crypto.generate_secret_token()

      headers = {
        'pSecretToken': f'{secret_token}'
      }

      response = requests.get(url, params=params, headers=headers, timeout=timeout, allow_redirects=True)
      response.raise_for_status()
      return response.content, response.status_code

    except Exception as ex:
      return None, str(ex)
