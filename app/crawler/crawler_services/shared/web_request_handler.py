from playwright.sync_api import sync_playwright
from raven.transport import requests
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.constants.enums import network_type
from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_instance.local_shared_model.rule_model import FetchProxy
from crawler.crawler_services.log_manager.log_controller import log
from crawler.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS
from crawler.crawler_services.shared.helper_method import helper_method


class webRequestManager:

  def __init__(self):
    pass

  @staticmethod
  def fetch(p_url, p_proxy, headers):
    try:
      if p_proxy is not None:
        proxy_url = next(iter(p_proxy.values()))
        ip_port = proxy_url.split('//')[1]
        ip, port = ip_port.split(':')
        proxy_host = p_proxy.get('host', ip)
        proxy_port = p_proxy.get('port', port)

        m_type = helper_method.get_network_type(p_url)
        if m_type == network_type.ONION:
          proxies = {
            "http": f"socks5h://{proxy_host}:{proxy_port}",
            "https": f"socks5h://{proxy_host}:{proxy_port}"
          }
        else:
          proxies = p_proxy
        response = requests.get(p_url, headers=headers, proxies=proxies, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT)
      else:
        response = requests.get(p_url, headers=headers, timeout=CRAWL_SETTINGS_CONSTANTS.S_URL_TIMEOUT)
      response.raise_for_status()
      return response.text, response.status_code, response.url

    except Exception as ex:
      return str(ex), None, None

  @staticmethod
  def load_headless_url(url, p_proxy, m_fetch_proxy: FetchProxy):
    try:
      with sync_playwright() as p:
        if m_fetch_proxy is FetchProxy.NONE:
          browser = p.chromium.launch(headless=True)
        else:
          proxy_url = next(iter(p_proxy.values()))
          ip_port = proxy_url.split('//')[1]
          ip, port = ip_port.split(':')
          proxy_host = p_proxy.get('host', ip)
          proxy_port = p_proxy.get('port', port)
          proxies = {"server": f"socks5://{proxy_host}:{proxy_port}"}
          browser = p.chromium.launch(proxy=proxies, headless=True)

        context = browser.new_context()
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page_source = page.content()
        browser.close()
        return page_source, True, url

    except requests.RequestException as ex:
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

  @staticmethod
  def request_server_post(url, data=None, params=None, timeout=1000):
    response = None
    try:
      token = redis_controller().invoke_trigger(REDIS_COMMANDS.S_GET_STRING, ["bearertoken", "", None])
      headers = {
        "Authorization": f"Bearer {token}",
      }

      response = requests.post(url, json=data, params=params, headers=headers, timeout=timeout)
      response.raise_for_status()
      return response.json(), response.status_code

    except Exception as ex:
      return None, str(ex)

    finally:
      if response is not None:
        response.close()

  @staticmethod
  def request_server_get(url, params=None, timeout=1000):
    try:
      token = redis_controller().invoke_trigger(REDIS_COMMANDS.S_GET_STRING, ["bearertoken", "", None])

      headers = {
        "Authorization": f"Bearer {token}",
      }

      response = requests.get(url, params=params, headers=headers, timeout=timeout, allow_redirects=True)
      response.raise_for_status()
      return response.content, response.status_code

    except Exception as ex:
      return None, str(ex)

  @staticmethod
  def request_token(url, username, password, timeout=1000):
    try:
      headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
      }

      payload = {
        'username': username,
        'password': password
      }

      response = requests.post(url, data=payload, headers=headers, timeout=timeout, allow_redirects=True)

      if response.status_code != 200:
        return None, f"HTTP {response.status_code}: {response.text}"

      try:
        data = response.json()
      except requests.exceptions.JSONDecodeError:
        return None, "Invalid JSON response from server"

      token = data.get("access_token")
      if not token:
        return None, "Token not found in response"

      return token, response.status_code

    except requests.exceptions.RequestException as ex:
      return None, f"Request failed: {ex}"