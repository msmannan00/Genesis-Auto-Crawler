import time

import pymongo
from crawler.crawler_instance.local_shared_model.url_model import url_model_list
from crawler.crawler_services.crawler_services.mongo_manager.mongo_enums import MONGODB_KEYS, MONGODB_COLLECTIONS, MONGODB_COMMANDS, MONGODB_PROPERTIES
from crawler.crawler_shared_directory.request_manager.request_handler import request_handler


class mongo_request_generator(request_handler):

  def __init__(self):
    pass

  def __on_install_index(self, p_urls):
    current_time = time.time()
    return [
      {
        MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_MONGO_INDEX_MODEL,
        MONGODB_KEYS.S_FILTER: {'m_url': url},
        MONGODB_KEYS.S_VALUE: {
          '$setOnInsert': {
            'analytics.m_failed_hits': 0,
            'analytics.m_duplicate_hits': 0,
            'analytics.m_low_yield_hits': 0
          },
          '$set': {
            'status.m_crawler_waiting': True,
            'installed_at': current_time,
            'status.m_live': True,
            'sub_url_parsed': [],
            'sub_url_pending': [],
            'image_url_parsed': [],
            'content': [],
            'document_url_parsed': [],
            'video_url_parsed': []
          }
        }
      }
      for url in p_urls
    ]

  def __on_fetch_index_url(self):
    return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_MONGO_INDEX_MODEL,
            MONGODB_KEYS.S_FILTER: {'status.m_crawler_waiting': True},
            MONGODB_PROPERTIES.S_SORT: ['installed_at', pymongo.ASCENDING],
            MONGODB_KEYS.S_VALUE: {'m_url': 1, '_id': 0}}

  def __on_fetch_index(self, p_url):
    return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_MONGO_INDEX_MODEL,
            MONGODB_KEYS.S_VALUE: '',
            MONGODB_KEYS.S_FILTER: {'m_url': p_url}}

  def __on_remove_dead_index(self, p_skip_url):
    return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_MONGO_INDEX_MODEL,
            MONGODB_KEYS.S_FILTER: {"status.m_live": {"$eq": False}, "m_url": {"$nin": p_skip_url}}}

  def __on_reset_live_status(self):
    return {
      MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_MONGO_INDEX_MODEL,
      MONGODB_KEYS.S_FILTER: {},
      MONGODB_KEYS.S_VALUE: {
        '$set': {'status.m_live': False}
      }
    }

  def __on_set_live_status(self, p_urls):
    return [
      {
        MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_MONGO_INDEX_MODEL,
        MONGODB_KEYS.S_FILTER: {'m_url': url},
        MONGODB_KEYS.S_VALUE: {
          '$set': {'status.m_live': True}
        }
      }
      for url in p_urls
    ]

  def __on_close_completed_index(self, p_request_model):
    return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_MONGO_INDEX_MODEL,
            MONGODB_KEYS.S_FILTER: {'m_url': {'$eq': p_request_model}}, MONGODB_KEYS.S_VALUE:
              {'$set': {'status.m_crawler_waiting': False, 'sub_url_parsed': [], 'sub_url_pending': [], 'image_url_parsed': [], 'content': [], 'document_url_parsed': [], 'video_url_parsed': []}}}

  def __update_index(self, p_request_url, sub_url_parsed, sub_url_pending):
    m_cached_url = url_model_list(sub_url_pending=sub_url_pending).model_dump()
    m_cached_url['sub_url_parsed'] = sub_url_parsed

    return {MONGODB_KEYS.S_DOCUMENT: MONGODB_COLLECTIONS.S_MONGO_INDEX_MODEL,
            MONGODB_KEYS.S_FILTER: {'m_url': {'$eq': p_request_url}}, MONGODB_KEYS.S_VALUE:
              {'$set': m_cached_url, '$push': {
                'document_url_parsed': {'$each': []},
                'video_url_parsed': {'$each': []},
                'image_url_parsed': {'$each': []}}}}

  def invoke_trigger(self, p_commands, p_data=None):
    if p_commands == MONGODB_COMMANDS.S_INSTALL_CRAWLABLE_URL:
      return self.__on_install_index(p_data)
    elif p_commands == MONGODB_COMMANDS.S_GET_CRAWLABLE_URL_DATA:
      return self.__on_fetch_index_url()
    elif p_commands == MONGODB_COMMANDS.S_RESET_CRAWLABLE_URL:
      return self.__on_reset_live_status()
    elif p_commands == MONGODB_COMMANDS.S_SET_CRAWLABLE_URL:
      return self.__on_set_live_status(p_data)
    elif p_commands == MONGODB_COMMANDS.S_REMOVE_DEAD_CRAWLABLE_URL:
      return self.__on_remove_dead_index(p_data[0])
    elif p_commands == MONGODB_COMMANDS.S_CLOSE_INDEX_ON_COMPLETE:
      return self.__on_close_completed_index(p_data[0])
    elif p_commands == MONGODB_COMMANDS.S_UPDATE_INDEX:
      return self.__update_index(p_data[0], p_data[1], p_data[2])
    elif p_commands == MONGODB_COMMANDS.S_GET_INDEX:
      return self.__on_fetch_index(p_data[0])
