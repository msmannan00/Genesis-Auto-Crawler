import importlib
import os
import sys
from typing import Optional, Any, Set

from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_instance.genbot_service.html_parse_manager import html_parse_manager
from crawler.crawler_instance.genbot_service.file_parse_manager import file_parse_manager
from crawler.crawler_instance.genbot_service.post_leak_model_tuner import post_leak_model_tuner
from crawler.crawler_instance.local_shared_model.leak_data_model import leak_data_model
from crawler.crawler_instance.local_shared_model.index_model import index_model
from crawler.crawler_instance.local_shared_model.url_model import url_model
from crawler.crawler_services.shared.helper_method import helper_method


class parse_controller:

    def __init__(self):
        self.leak_extractor_instance = None
        self.post_leak_model_instance = post_leak_model_tuner()
        self.module_cache = {}
        self.file_parse_mgr = None

    def _get_file_parse_manager(self):
        if self.file_parse_mgr is None:
            self.file_parse_mgr = file_parse_manager()
        return self.file_parse_mgr

    def on_parse_html(self, p_html: str, p_request_model: url_model) -> index_model:
        m_parsed_model = self.__on_html_parser_invoke(p_html, p_request_model)
        if CRAWL_SETTINGS_CONSTANTS.S_GENERIC_FILE_VERIFICATION_ALLOWED:
            return self._get_file_parse_manager().parse_generic_files(m_parsed_model)
        else:
            return m_parsed_model

    def on_parse_leaks(self, p_html: str, p_request_model: url_model) -> tuple[None, bool, bool] | tuple[leak_data_model, Set[str], bool]:
        data_model, m_sub_url = self.__on_leak_parser_invoke(p_html, p_request_model)
        if data_model is not None:
            parsed_data, m_sub_url = self._get_file_parse_manager().parse_leak_files(data_model), m_sub_url
            return parsed_data, m_sub_url, True
        else:
            data_model = leak_data_model(
                cards_data=[],
                contact_link="",
                base_url="",
            )
            return data_model, m_sub_url, len(m_sub_url)>0

    @staticmethod
    def __on_html_parser_invoke(p_html: str, p_request_model: url_model) -> index_model:
        return html_parse_manager(p_html, p_request_model).parse_html_files()

    def __on_leak_parser_invoke(self, p_html, p_request_model: url_model) -> tuple[Optional[Any], Set[str]]:
        if self.leak_extractor_instance is not None:
            data_model, m_sub_url = self.leak_extractor_instance.parse_leak_data(p_html, p_request_model.m_url)
            data_model.m_network = str(helper_method.get_network_type(p_request_model.m_url).value)
            return self.post_leak_model_instance.process(data_model, m_sub_url)
        else:
            return None, set()

    def on_init_leak_parser(self, p_data_url):
        if not self.leak_extractor_instance:
            class_name = "_"+helper_method.get_host_name(p_data_url)
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
