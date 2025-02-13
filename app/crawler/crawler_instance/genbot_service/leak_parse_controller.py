import importlib
import json
import os
import sys
from threading import Timer
from typing import Tuple, Dict
from bs4 import BeautifulSoup
from httpcore import TimeoutException
from playwright.sync_api import sync_playwright

from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_instance.genbot_service.file_parse_manager import file_parse_manager
from crawler.crawler_instance.local_interface_model.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model.leak_data_model import leak_data_model
from crawler.crawler_instance.local_shared_model.rule_model import FetchProxy
from crawler.crawler_services.elastic_manager.elastic_controller import elastic_controller
from crawler.crawler_services.elastic_manager.elastic_enums import ELASTIC_CRUD_COMMANDS, ELASTIC_REQUEST_COMMANDS, ELASTIC_CONNECTIONS
from crawler.crawler_services.log_manager.log_controller import log
from crawler.crawler_services.shared.helper_method import helper_method


class leak_parse_controller:

  def __init__(self):
    self.__m_proxy = {}
    self.file_parse_mgr = None
    self.leak_extractor_instance = None
    self.module_cache = {}
    self.__elastic_controller_instance = elastic_controller()

    self.__m_proxy = {}
    self.__m_tor_id = - 1

  def _get_file_parse_manager(self):
    if self.file_parse_mgr is None:
      self.file_parse_mgr = file_parse_manager()
    return self.file_parse_mgr

  def init(self, p_proxy, p_tor_id):
    self.__m_proxy, self.__m_tor_id = p_proxy, p_tor_id

  def on_leak_parser_invoke(self) -> Dict[str, str]:
    data_model, generic_parse_mapping = self.__parse_leak_data(self.__m_proxy, self.leak_extractor_instance)
    return generic_parse_mapping

  def on_init_leak_parser(self, p_data_url):
    if not self.leak_extractor_instance:
      class_name = "_" + helper_method.get_host_name(p_data_url)
      try:
        module_path = f"raw.parsers.local.{class_name}"

        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if parent_dir not in sys.path:
          sys.path.append(parent_dir)

        if class_name not in self.module_cache:
          module = importlib.import_module(module_path)
          class_ = getattr(module, class_name)
          self.module_cache[class_name] = class_()

        self.leak_extractor_instance = self.module_cache[class_name]

      except Exception as ex:
        pass

  def trigger_server(self, model: leak_data_model):
    if len(model.cards_data)>0:
      for item in model.cards_data:
        item.m_network_type = helper_method.get_network_type(item)
      model.m_network = helper_method.get_network_type(model.base_url)
      m_paresed_request_data = model.model_dump()
      self.__elastic_controller_instance.invoke_trigger(ELASTIC_CRUD_COMMANDS.S_INDEX, [ELASTIC_REQUEST_COMMANDS.S_INDEX, m_paresed_request_data, ELASTIC_CONNECTIONS.S_INDEX_LEAK])

  def __parse_leak_data(self, proxy: dict, model: leak_extractor_interface) -> Tuple[leak_data_model, Dict[str, str]]:
    parsed_length = 0
    default_data_model = leak_data_model(
      cards_data=[],
      contact_link=model.contact_page(),
      base_url=model.base_url,
      content_type=["leak"]
    )

    raw_parse_mapping = {}
    timeout_flag = {"value": False}

    def block_media(route):
      request_url = route.request.url.lower()

      if any(request_url.startswith(scheme) for scheme in ["data:image", "data:video", "data:audio"]) or \
          route.request.resource_type in ["image", "media", "font", "stylesheet"]:
        route.abort()
      else:
        route.continue_()

    def terminate_browser():
      nonlocal browser
      timeout_flag["value"] = True
      if browser:
        try:
          print("Timeout reached. Closing browser and terminating tasks.")
          browser.close()
        except Exception:
          pass

    try:
      with sync_playwright() as p:
        if model.rule_config.m_fetch_proxy is FetchProxy.NONE:
          browser = p.chromium.launch(headless=True)
        else:
          playwright_proxy = {
            'server': proxy['http'].replace('socks5h', 'socks5'),
          }
          browser = p.chromium.launch(proxy=playwright_proxy, headless=True)

        context = browser.new_context()
        context.set_default_timeout(60000)
        context.set_default_navigation_timeout(60000)
        timeout_timer = Timer(model.rule_config.m_timeout, terminate_browser)
        timeout_timer.start()

        try:
          page = context.new_page()
          page.route("**/*", block_media)

          def capture_response(response):
            nonlocal parsed_length
            if response.request.resource_type == "document" and response.ok and response.url not in raw_parse_mapping:
              raw_parse_mapping[response.url] = response.text()
              log.g().s(MANAGE_MESSAGES.S_LOCAL_URL_PARSED + " : leak_counter " + "-1" + " : " + str(self.__m_tor_id) + " : " + response.url)

            current_length = len(model.card_data)
            if current_length >= parsed_length + 10:
              for i in range(parsed_length, current_length, 10):
                batch_cards = model.card_data[i:i + 10]
                default_data_model_temp = leak_data_model(cards_data=batch_cards, contact_link=model.contact_page(), base_url=model.base_url, content_type=["leak"])

                self.trigger_server(default_data_model_temp)
              parsed_length = current_length

          page.on("response", capture_response)
          page.goto(model.seed_url, wait_until="networkidle")

          if timeout_flag["value"]:
            raise TimeoutException("Timeout occurred during navigation.")

          model.soup = BeautifulSoup(page.content(), 'html.parser')
          raw_parse_mapping[page.url] = page.content()
          model.parse_leak_data(page)
        except Exception:
          pass
        finally:
          timeout_timer.cancel()

    except Exception as e:
      print(f"Unexpected Error: {e}")

    default_data_model.cards_data = model.card_data[-10:]
    self.trigger_server(default_data_model)

    return default_data_model, raw_parse_mapping
