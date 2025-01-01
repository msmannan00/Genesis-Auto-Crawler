from urllib.parse import urlparse

from crawler.constants.constant import CRAWL_SETTINGS_CONSTANTS

parsed_url = urlparse(CRAWL_SETTINGS_CONSTANTS.S_SEARCH_SERVER)
vv = (parsed_url.hostname)
tt = (parsed_url.port)
print(vv)
print(tt)

