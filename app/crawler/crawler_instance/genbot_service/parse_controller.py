import importlib
import os
import sys
from typing import Optional, Any

from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_instance.genbot_service.html_parse_manager import html_parse_manager
from crawler.crawler_instance.genbot_service.file_parse_manager import file_parse_manager
from crawler.crawler_instance.genbot_service.post_leak_model_tuner import post_leak_model_tuner
from crawler.crawler_instance.helper_services.helper_method import helper_method
from crawler.crawler_instance.local_interface_model.leak_extractor_interface import leak_extractor_interface
from crawler.crawler_instance.local_shared_model import leak_data_model
from crawler.crawler_instance.local_shared_model.index_model import index_model
from crawler.crawler_instance.local_shared_model.url_model import url_model


class parse_controller:

    def __init__(self):
        self.leak_extractor_instance = None

    def on_parse_html(self, p_html: str, p_request_model: url_model) -> index_model:
        m_parsed_model = self.__on_html_parser_invoke(p_html, p_request_model)
        if CRAWL_SETTINGS_CONSTANTS.S_GENERIC_FILE_VERIFICATION_ALLOWED:
            return file_parse_manager().parse_generic_files(m_parsed_model)
        else:
            return m_parsed_model

    def on_parse_leaks(self, p_html: str, m_url: str) -> tuple[None, bool] | tuple[leak_data_model, bool]:
        data_model, m_sub_url = self.__on_leak_parser_invoke(p_html, m_url)
        if CRAWL_SETTINGS_CONSTANTS.S_GENERIC_FILE_VERIFICATION_ALLOWED and data_model is not None:
            return file_parse_manager().parse_leak_files(data_model), m_sub_url
        else:
            return data_model, m_sub_url

    def __on_html_parser_invoke(self, p_html: str, p_request_model: url_model) -> index_model:
        return html_parse_manager(p_html, p_request_model).parse_html_files()

    def __on_leak_parser_invoke(self, p_html, p_data_url: str) -> tuple[Optional[Any], bool]:
        if not self.leak_extractor_instance:
            class_name = helper_method.get_host_name(p_data_url)  # Get the host name
            try:
                module_path = f"raw.{class_name}"

                parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                if parent_dir not in sys.path:
                    sys.path.append(parent_dir)

                module = importlib.import_module(module_path)
                class_ = getattr(module, class_name)
                self.leak_extractor_instance: leak_extractor_interface = class_()
            except Exception:
                return None, False

        data_model, m_sub_url = self.leak_extractor_instance.parse_leak_data(p_html, p_data_url)
        return post_leak_model_tuner.get_instance().process(data_model, m_sub_url)
