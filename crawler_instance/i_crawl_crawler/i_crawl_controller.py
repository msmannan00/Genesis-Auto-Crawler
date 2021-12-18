# Local Imports
import time

from crawler_instance.constants.constant import CRAWL_SETTINGS_CONSTANTS
from crawler_instance.constants.strings import MESSAGE_STRINGS
from crawler_instance.crawl_controller.crawl_enums import CRAWLER_STATUS
from crawler_instance.i_crawl_crawler.i_crawl_enums import ICRAWL_CONTROLLER_COMMANDS, CRAWL_STATUS_TYPE
from crawler_instance.log_manager.log_controller import log
from crawler_instance.shared_model.request_handler import request_handler
from crawler_services.crawler_services.content_duplication_manager.content_duplication_controller_local import \
    content_duplication_controller_local
from crawler_services.crawler_services.content_duplication_manager.content_duplication_enums import \
    CONTENT_DUPLICATION_MANAGER
from crawler_services.helper_services.duplication_handler import duplication_handler
from crawler_services.helper_services.helper_method import helper_method
from crawler_instance.i_crawl_crawler.parse_controller import parse_controller
from crawler_instance.i_crawl_crawler.web_request_handler import webRequestManager


class i_crawl_controller(request_handler):

    __m_web_request_handler = None
    __m_duplication_handler = None
    __m_content_duplication_handler = None
    __m_request_model = None

    __m_parsed_model = None
    __m_thread_status = CRAWLER_STATUS.S_RUNNING
    __m_save_to_mongodb = False
    __m_url_status = CRAWL_STATUS_TYPE.S_NONE

    def __init__(self):
        self.__m_duplication_handler = duplication_handler()
        self.__m_content_duplication_handler = content_duplication_controller_local()
        self.__m_web_request_handler = webRequestManager()

    def __clean_sub_url(self, p_parsed_model):
        m_sub_url_filtered = []
        for m_sub_url in  p_parsed_model.m_sub_url:
            if self.__m_duplication_handler.validate_duplicate(m_sub_url) is False:
                self.__m_duplication_handler.insert(m_sub_url)
                m_sub_url_filtered.append(m_sub_url)
        p_parsed_model.m_sub_url = m_sub_url_filtered


        return p_parsed_model

    # Web Request To Get Physical URL HTML
    def __trigger_url_request(self, p_request_model):
        __m_save_to_mongodb = False
        m_html_parser = parse_controller()
        m_redirected_url, response, html = self.__m_web_request_handler.load_url(p_request_model.m_url)
        if response is True:
            m_status, m_parsed_model, m_url_status = m_html_parser.on_parse_html(html, p_request_model)
            self.__m_url_status = m_url_status
            if m_status is False:
                return None

            m_redirected_url = helper_method.normalize_slashes(m_redirected_url)
            m_redirected_requested_url = helper_method.normalize_slashes(p_request_model.m_url)
            if m_redirected_url == m_redirected_requested_url or m_redirected_url != m_redirected_requested_url and self.__m_duplication_handler.validate_duplicate(m_redirected_url) is False:
                self.__m_duplication_handler.insert(m_redirected_url)

                m_status = self.__m_content_duplication_handler.invoke_trigger(CONTENT_DUPLICATION_MANAGER.S_VALIDATE, [m_parsed_model.m_title, m_parsed_model.m_description, m_parsed_model.m_content_type])
                if m_status is False and m_parsed_model.m_validity_score >= 10 and (len(m_parsed_model.m_description) > 0) and response:
                    self.__m_duplication_handler.insert(m_parsed_model.m_base_url_model.m_redirected_host)
                    self.__m_save_to_mongodb = True
                    self.__m_content_duplication_handler.invoke_trigger(CONTENT_DUPLICATION_MANAGER.S_INSERT, [m_parsed_model.m_title, m_parsed_model.m_description, m_parsed_model.m_content_type])
                else:
                    log.g().w(MESSAGE_STRINGS.S_LOW_YIELD_URL + " : " + p_request_model.m_url)
                self.__m_url_status = CRAWL_STATUS_TYPE.S_LOW_YIELD

            m_parsed_model = self.__clean_sub_url(m_parsed_model)

            return m_parsed_model

        self.__m_url_status = CRAWL_STATUS_TYPE.S_FETCH_ERROR
        return None

    # Wait For Crawl Manager To Provide URL From Queue
    def __start_crawler_instance(self, p_request_model):
        self.__invoke_thread(True, p_request_model)
        while self.__m_thread_status in [CRAWLER_STATUS.S_RUNNING, CRAWLER_STATUS.S_PAUSE]:
            time.sleep(CRAWL_SETTINGS_CONSTANTS.S_ICRAWL_INVOKE_DELAY)
            # try:
            if self.__m_thread_status == CRAWLER_STATUS.S_RUNNING:
                self.__m_parsed_model = self.__trigger_url_request(self.__m_request_model)
                self.__m_thread_status = CRAWLER_STATUS.S_PAUSE
            # except Exception as ex:
            #     self.__m_thread_status = CRAWLER_STATUS.S_PAUSE
            #     print(ex.__traceback__)

    # Crawl Manager Makes Request To Get Crawl duplicationHandlerService
    def __get_crawled_data(self):
        return self.__m_parsed_model, self.__m_thread_status, self.__m_save_to_mongodb, self.__m_url_status, self.__m_request_model

    # Crawl Manager Awakes Crawler Instance From Sleep
    def __invoke_thread(self, p_status, p_request_model):
        if p_status is True:
            self.__m_request_model = p_request_model
            self.__m_thread_status = CRAWLER_STATUS.S_RUNNING
        else:
            self.__m_thread_status = CRAWLER_STATUS.S_STOP

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE:
            self.__start_crawler_instance(p_data[0])
        if p_command == ICRAWL_CONTROLLER_COMMANDS.S_GET_CRAWLED_DATA:
            return self.__get_crawled_data()
        if p_command == ICRAWL_CONTROLLER_COMMANDS.S_INVOKE_THREAD:
            return self.__invoke_thread(p_data[0], p_data[1])
