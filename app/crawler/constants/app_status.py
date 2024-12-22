# External DB Queue Exists And Not Empty
from crawler.crawler_instance.proxies.tor_controller.tor_enums import TOR_STATUS


class APP_STATUS:
  DOCKERIZED_RUN = True
  LOCAL_LOGS = True
  S_TOR_STATUS = TOR_STATUS.S_READY
  S_INTERNET_STATUS = False

