# Local Imports
import filecmp
import json

from crawler.constants.constant import RAW_PATH_CONSTANTS
from crawler.constants.strings import MANAGE_MESSAGES
from crawler.crawler_services.crawler_services.elastic_manager.elastic_controller import elastic_controller
from crawler.crawler_services.crawler_services.elastic_manager.elastic_enums import ELASTIC_CRUD_COMMANDS, ELASTIC_REQUEST_COMMANDS, ELASTIC_CONNECTIONS
from crawler.crawler_services.crawler_services.redis_manager.redis_controller import redis_controller
from crawler.crawler_services.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, REDIS_KEYS
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler
from crawler.crawler_instance.genbot_service.genbot_enums import ICRAWL_CONTROLLER_COMMANDS
from crawler.crawler_services.web_request_handler import webRequestManager
from crawler.crawler_services.helper_services.duplication_handler import duplication_handler
from crawler.crawler_shared_directory.log_manager.log_controller import log
from crawler.crawler_services.helper_services.helper_method import helper_method
import hashlib
from bs4 import BeautifulSoup
import os
import sys


class genbot_unique_controller(request_handler):

  def __init__(self):
    self.__task_id = -1
    self.m_url_duplication_handler = duplication_handler()
    self.__m_web_request_handler = webRequestManager()
    self.__m_parsed_list = []

    self.__m_tor_id = - 1
    self.__m_proxy = {}

  def init(self, p_proxy, p_tor_id):
    self.__m_proxy, self.__m_tor_id = p_proxy, p_tor_id

  def __trigger_url_request(self, p_url):
    try:
      log.g().i(MANAGE_MESSAGES.S_UNIQUE_PARSING_URL_STARTED + " : " + p_url)
      m_redirected_url, m_response, m_raw_html = self.__m_web_request_handler.load_url(p_url, self.__m_proxy)

      if m_response is True:
        soup = BeautifulSoup(m_raw_html, 'html.parser')
        extracted_text = soup.get_text()
        substring_text = extracted_text[0:500]
        unique_hash = hashlib.sha256(substring_text.encode('utf-8')).hexdigest()
        if self.m_url_duplication_handler.validate_duplicate(unique_hash):
          return False, True
        else:
          self.m_url_duplication_handler.insert(p_url)
          self.__index_url(p_url)
          return True, True
      else:
        return False, False

    except Exception as ex:
      log.g().e(MANAGE_MESSAGES.S_LOAD_URL_ERROR + " : " + str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + str(ex))
      return False, True

  def __index_url(self, m_url):
    file_path = os.path.join(RAW_PATH_CONSTANTS.UNIQUE_CRAWL_DIRECTORY, 'hosts_new.txt')
    try:
      with open(file_path, 'a') as file:
        file.write(m_url + '\n')
      log.g().i(MANAGE_MESSAGES.S_UNIQUE_INDEX_UPDATED_SUCCESSFULLY + " : " + f"Written to file: {m_url}")
    except Exception as e:
      log.g().e(MANAGE_MESSAGES.S_UNIQUE_INDEX_UPDATE_FAILED + " : " + f"Failed to write to file: {e}")

  def __update_global_index(self):
    file_path_new = os.path.join(RAW_PATH_CONSTANTS.UNIQUE_CRAWL_DIRECTORY, 'hosts_new.txt')
    file_path_old = os.path.join(RAW_PATH_CONSTANTS.UNIQUE_CRAWL_DIRECTORY, 'hosts.txt')

    try:
      if os.path.exists(file_path_old) and filecmp.cmp(file_path_new, file_path_old, shallow=False):
        with open(file_path_new, 'w'):
          pass
      else:
        os.replace(file_path_new, file_path_old)
        elastic_controller().invoke_trigger(ELASTIC_CRUD_COMMANDS.S_INDEX, [ELASTIC_REQUEST_COMMANDS.S_UNIQUE_INDEX, json.dumps(self.__m_parsed_list), ELASTIC_CONNECTIONS.S_CRAWL_UNIQUE_INDEX])
        with open(file_path_new, 'w'):
          pass
    except Exception as ex:
      pass

  def start_crawler_instance(self, p_request_url_list):
      for m_url in p_request_url_list:
        try:
          m_url = helper_method.on_clean_url(m_url)
          m_status = False
          m_failure_count = 0
          while m_failure_count<3:
            m_status, m_web_status = self.__trigger_url_request(m_url)
            if m_web_status is False:
              m_failure_count += 1
              continue
            else:
              break
          if m_status:
            self.__m_parsed_list.append(m_url)
            log.g().i(MANAGE_MESSAGES.S_UNIQUE_PARSING_URL_FINISHED + " : " + str(len(self.__m_parsed_list)))
        except Exception as ex:
          log.g().e(str(self.__task_id) + " : " + str(self.__m_tor_id) + " : " + str(ex))
      self.__update_global_index()

  def invoke_trigger(self, p_command, p_data=None):
    if p_command == ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE:
      self.start_crawler_instance(p_data[0])
    if p_command == ICRAWL_CONTROLLER_COMMANDS.S_INIT_CRAWLER_INSTANCE:
      self.init(p_data[0], p_data[1])


def genbot_unique_instance(p_url_list, p_proxy, p_tor_id):
  redis_controller_instance = redis_controller()
  status = redis_controller_instance.invoke_trigger(REDIS_COMMANDS.S_GET_BOOL, [REDIS_KEYS.UNIQIE_CRAWLER_RUNNING, None, None])
  if not status:
    log.g().i(MANAGE_MESSAGES.S_UNIQUE_PARSING_STARTED + " : " + str(status))
    redis_controller_instance.invoke_trigger(REDIS_COMMANDS.S_SET_BOOL, [REDIS_KEYS.UNIQIE_CRAWLER_RUNNING, True, None])
    m_crawler = genbot_unique_controller()
    m_crawler.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_INIT_CRAWLER_INSTANCE, [p_proxy, p_tor_id])
    try:
      m_crawler.invoke_trigger(ICRAWL_CONTROLLER_COMMANDS.S_START_CRAWLER_INSTANCE, [p_url_list])
    except Exception as ex:
      log.g().e(MANAGE_MESSAGES.S_GENBOT_ERROR + " : " + str(ex))
    finally:
      redis_controller_instance.invoke_trigger(REDIS_COMMANDS.S_SET_BOOL, [REDIS_KEYS.UNIQIE_CRAWLER_RUNNING, False, None])
      del m_crawler
      log.g().s(MANAGE_MESSAGES.S_UNIQUE_PARSING_COMPLETE)
  else:
    log.g().i(MANAGE_MESSAGES.S_UNIQUE_PARSING_PENDING)

def prepare_and_fetch_data(url):
  os.makedirs(RAW_PATH_CONSTANTS.UNIQUE_CRAWL_DIRECTORY, exist_ok=True)
  helper_method.clear_hosts_file(os.path.join(RAW_PATH_CONSTANTS.UNIQUE_CRAWL_DIRECTORY, 'hosts.txt'))
  helper_method.clear_hosts_file(os.path.join(RAW_PATH_CONSTANTS.UNIQUE_CRAWL_DIRECTORY, 'hosts_new.txt'))

  web_request_manager = webRequestManager()
  file_content, status_or_error = web_request_manager.request_server_get(url)

  if status_or_error == 200:
    return file_content.decode('utf-8').splitlines()
  else:
    log.g().e(MANAGE_MESSAGES.S_UNIQUE_INDEX_FAILED)
    return None
