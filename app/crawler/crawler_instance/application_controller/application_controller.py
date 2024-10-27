import warnings
from abc import ABC

from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_instance.application_controller.application_enums import APPICATION_COMMANDS
from crawler.crawler_instance.crawl_controller.crawl_enums import CRAWL_CONTROLLER_COMMANDS
from crawler.crawler_instance.crawl_controller.crawl_controller import crawl_controller
from crawler.crawler_instance.tor_controller.tor_controller import tor_controller
from crawler.crawler_services.helper_services.helper_method import helper_method
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler

warnings.filterwarnings("ignore", category=DeprecationWarning)

import time

class application_controller(request_handler, ABC):
    __instance = None
    __m_crawl_controller = None

    @staticmethod
    def get_instance():
        if application_controller.__instance is None:
            application_controller()
        return application_controller.__instance

    def __init__(self):
        if application_controller.__instance is not None:
            raise Exception(MANAGE_MESSAGES.S_SINGLETON_EXCEPTION)
        else:
            self.__m_crawl_controller = crawl_controller()
            self.__tor_controller = tor_controller.get_instance()
            application_controller.__instance = self

    def __initializations(self, p_command):
        if p_command == APPICATION_COMMANDS.S_START_APPLICATION_DIRECT:
            mongo_status = helper_method.check_service_status("MongoDB", "localhost", 27017)
            redis_status = helper_method.check_service_status("Redis", "localhost", 6379)
            if not mongo_status or not redis_status:
                exit(0)

    def __wait_for_tor_bootstrap(self):
        non_bootstrapped_tor_instances = self.__tor_controller.get_non_bootstrapped_tor_instances()
        while non_bootstrapped_tor_instances:
            instance_status = ", ".join([f"{ip_port} (phase: {phase})" for ip_port, phase in non_bootstrapped_tor_instances])
            log.g().i(f"Waiting for Tor instances to bootstrap: {instance_status}")
            time.sleep(10)
            non_bootstrapped_tor_instances = self.__tor_controller.get_non_bootstrapped_tor_instances()

        log.g().i("All Tor instances have bootstrapped successfully.")

    def __on_start(self, p_command):
        self.__initializations(p_command)
        self.__wait_for_tor_bootstrap()
        log.g().i(MANAGE_MESSAGES.S_APPLICATION_STARTING)
        self.__m_crawl_controller.invoke_trigger(CRAWL_CONTROLLER_COMMANDS.S_RUN_CRAWLER)

    def invoke_triggers(self, p_command):
        if p_command == APPICATION_COMMANDS.S_START_APPLICATION_DIRECT:
            return self.__on_start(p_command)
        elif p_command == APPICATION_COMMANDS.S_START_APPLICATION_DOCKERISED:
            return self.__on_start(p_command)
