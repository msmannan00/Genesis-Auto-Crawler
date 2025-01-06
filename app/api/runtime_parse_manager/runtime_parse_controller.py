import asyncio
import importlib
import json
import os
import sys
from linecache import cache

from api.runtime_parse_manager.runtime_parse_enum import RUNTIME_PARSE_REQUEST_QUERIES, RUNTIME_PARSE_REQUEST_COMMANDS
from crawler.crawler_instance.local_shared_model.collector_data_model import collector_data_model
from playwright.async_api import async_playwright
from typing import Optional
from crawler.crawler_instance.local_shared_model.rule_model import FetchProxy
from crawler.crawler_instance.proxies.tor_controller.tor_controller import tor_controller
from crawler.crawler_instance.proxies.tor_controller.tor_enums import TOR_COMMANDS


class runtime_parse_controller:

    def __init__(self):
        self.module_cache = {}
        self.driver = None

    @staticmethod
    async def _initialize_webdriver(use_proxy: FetchProxy = FetchProxy.TOR) -> Optional[object]:

        tor_proxy = None
        if use_proxy == FetchProxy.TOR:
            tor_proxy, tor_id = tor_controller.get_instance().invoke_trigger(TOR_COMMANDS.S_PROXY, [])

        proxy_url = next(iter(tor_proxy.values()))
        ip_port = proxy_url.split('//')[1]
        ip, port = ip_port.split(':')
        proxy_host = tor_proxy.get('host', ip)
        proxy_port = tor_proxy.get('port', port)
        proxies = {"server": f"socks5://{proxy_host}:{proxy_port}"}


        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True, proxy=proxies)

        context = await browser.new_context()
        return context

    # async def _initialize_webdriver(use_proxy: bool = True) -> Optional[object]:
    #     if use_proxy:
    #         tor_proxy = "socks5://127.0.0.1:9150"
    #         playwright = await async_playwright().start()
    #         browser = await playwright.chromium.launch(headless=False,
    #                                                    proxy={"server": tor_proxy} if tor_proxy else None)
    #     else:
    #         playwright = await async_playwright().start()
    #         browser = await playwright.chromium.launch(headless=False)
    #
    #     context = await browser.new_context()
    #     return context

    @staticmethod
    def create_collector_model(base_url, content_type):
        return collector_data_model(base_url=base_url, content_type=content_type)

    async def get_email_username(self, query):
        result = []
        try:
            if self.driver is None:
                self.driver = await self._initialize_webdriver()
        except Exception as e:
            return json.dumps(result)

        for parser in RUNTIME_PARSE_REQUEST_QUERIES.S_USERNAME:
            try:
                parse_script = self.on_init_leak_parser(parser)
                query["url"] = parse_script.base_url
                response = await parse_script.parse_leak_data(query, self.driver)
                if len(response.cards_data)>0:
                    result.append(response.model_dump())
            except Exception as e:
                self.driver = None
                pass

        return json.dumps(result)

    def on_init_leak_parser(self, file_name):
        class_name = "_" + file_name
        try:
            module_path = f"raw.parsers.dynamic.{class_name}"
            parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            if class_name not in self.module_cache:
                module = importlib.import_module(module_path)
                class_ = getattr(module, class_name)
                self.module_cache[class_name] = class_()
            return self.module_cache[class_name]

        except Exception as ex:
            return None

    async def invoke_trigger(self, command, data=None):
        if command == RUNTIME_PARSE_REQUEST_COMMANDS.S_PARSE_USERNAME:
            return await self.get_email_username(data)
#
# async def main():
#     url = "http://breachdbsztfykg2fdaq2gnqnxfsbj5d35byz3yzj73hazydk4vq72qd.onion/"
#     email = "msmannan00@gmail.com"
#     username = "msmannan00"
#     query = {"url": url, "email": email, "username": username}
#
#     try:
#         result = await runtime_parse_controller().invoke_trigger(RUNTIME_PARSE_REQUEST_COMMANDS.S_PARSE_USERNAME, query)
#         print(result)
#     except Exception as e:
#         print("Error occurred:", e)
#     finally:
#         pass
#
#
# if __name__ == "__main__":
#     asyncio.run(main())