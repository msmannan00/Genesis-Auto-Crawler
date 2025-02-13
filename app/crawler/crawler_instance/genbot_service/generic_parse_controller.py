import json
from typing import Dict

from crawler.crawler_instance.genbot_service.html_parse_manager import html_parse_manager
from crawler.crawler_instance.genbot_service.file_parse_manager import file_parse_manager
from crawler.crawler_instance.local_shared_model.index_model import index_model
from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel, FetchConfig
from crawler.crawler_instance.local_shared_model.url_model import url_model, url_model_init
from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler.crawler_services.elastic_manager.elastic_controller import elastic_controller
from crawler.crawler_services.elastic_manager.elastic_enums import ELASTIC_CRUD_COMMANDS, ELASTIC_REQUEST_COMMANDS, ELASTIC_CONNECTIONS
from crawler.crawler_services.shared.duplication_handler import duplication_handler
from crawler.crawler_services.shared.helper_method import helper_method
from crawler.crawler_services.shared.web_request_handler import webRequestManager
from crawler.crawler_services.log_manager.log_controller import log


class generic_parse_controller:

    def __init__(self):
        self.__m_url_duplication_handler = duplication_handler()
        self.__m_web_request_handler = webRequestManager()
        self.__m_rule_model = RuleModel(m_fetch_config=FetchConfig.REQUESTS)
        self.__elastic_controller_instance = elastic_controller()

        self.__m_unparsed_url = []
        self.__m_proxy = {}
        self.__file_parse_mgr = None
        self.__m_network_type = None
        self.__task_id = -1
        self.__m_tor_id = - 1

    def on_clear(self):
        self.__m_url_duplication_handler.clear_filter()
        self.__m_url_duplication_handler = None
        self.__m_web_request_handler = None
        del self.__m_url_duplication_handler
        del self.__m_web_request_handler


    def init(self, p_proxy, p_tor_id):
        self.__m_proxy, self.__m_tor_id = p_proxy, p_tor_id

    def _get_file_parse_manager(self):
        if self.__file_parse_mgr is None:
            self.__file_parse_mgr = file_parse_manager()
        return self.__file_parse_mgr

    def __on_parse_html(self, p_html: str, p_request_model: url_model) -> index_model:
        m_parsed_model = self.__on_html_parser_invoke(p_html, p_request_model)
        if CRAWL_SETTINGS_CONSTANTS.S_GENERIC_FILE_VERIFICATION_ALLOWED:
            return self._get_file_parse_manager().parse_generic_files(m_parsed_model)
        else:
            return m_parsed_model

    @staticmethod
    def __on_html_parser_invoke(p_html: str, p_request_model: url_model) -> index_model:
        return html_parse_manager(p_html, p_request_model).parse_html_files()

    def __trigger_url_request(self, p_request_model: url_model, proxy, task_id, tor_id, raw_html=None):
        try:
            log.g().i(MANAGE_MESSAGES.S_PARSING_STARTING + f" : {task_id} : {tor_id} : {p_request_model.m_url}")
            if raw_html is not None:
                m_redirected_url = p_request_model.m_url
                m_response = True
                m_raw_html = raw_html
            else:
                m_redirected_url, m_response, m_raw_html = self.__m_web_request_handler.load_url(p_request_model.m_url, proxy)

            if m_response is True:
                m_parsed_model = self.__on_parse_html(m_raw_html, p_request_model)

                if m_parsed_model is not None:
                    if helper_method.get_host_name(m_redirected_url) == helper_method.get_host_name(p_request_model.m_url):
                        self.__elastic_controller_instance.invoke_trigger(
                           ELASTIC_CRUD_COMMANDS.S_INDEX, [ELASTIC_REQUEST_COMMANDS.S_INDEX, m_parsed_model.model_dump(), ELASTIC_CONNECTIONS.S_INDEX_GENERIC]
                        )
                        log.g().s(MANAGE_MESSAGES.S_LOCAL_URL_PARSED + " : " + str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + m_redirected_url)
                        return m_parsed_model, m_parsed_model.m_sub_url
                    else:
                        return None, None
                else:
                    return None, None
            else:
                log.g().w(MANAGE_MESSAGES.S_FAILED_URL_ERROR + f" : {task_id} : {tor_id} : {p_request_model.m_url}")
                return None, None
        except Exception as ex:
            log.g().e(MANAGE_MESSAGES.S_LOAD_URL_ERROR + f" : {task_id} : {tor_id} : {str(ex)}")
            return None, None

    def start_custom_crawler_instance(self, parse_data: Dict[str, str]):
        for url, html_content in parse_data.items():
            p_request_model = url_model_init(url, CRAWL_SETTINGS_CONSTANTS.S_DEFAULT_DEPTH, helper_method.get_network_type(url))
            self.__trigger_url_request(p_request_model, self.__m_proxy, self.__task_id, self.__m_tor_id, raw_html=html_content)

    def start_crawler_instance(self, p_request_url):
        p_request_url = helper_method.on_clean_url(p_request_url)
        self.__task_id = ""
        m_host_crawled = False
        m_failure_count = 0
        self.__m_network_type = helper_method.get_network_type(p_request_url)
        self.__m_unparsed_url.append(url_model_init(p_request_url, CRAWL_SETTINGS_CONSTANTS.S_DEFAULT_DEPTH, self.__m_network_type))
        while len(self.__m_unparsed_url) > 0:
            item = self.__m_unparsed_url.__getitem__(0)
            m_parsed_model, m_sub_url = self.__trigger_url_request(item, self.__m_proxy, self.__task_id, self.__m_tor_id)

            if m_parsed_model is None:
                if not m_host_crawled:
                    if m_failure_count > 2:
                        _ = self.__m_unparsed_url.pop(0)
                    else:
                        m_failure_count += 1
                    continue

            if m_parsed_model is not None and item.m_depth < CRAWL_SETTINGS_CONSTANTS.S_MAX_ALLOWED_DEPTH:
                for sub_url in list(m_sub_url)[0:CRAWL_SETTINGS_CONSTANTS.S_SUB_URL_DEPTH]:
                    if self.__m_url_duplication_handler.is_duplicate(sub_url) is False:
                        self.__m_url_duplication_handler.insert(sub_url)
                        self.__m_unparsed_url.append(url_model_init(sub_url, item.m_depth + 1, self.__m_network_type))

            m_host_crawled = True
            self.__m_unparsed_url.pop(0)
