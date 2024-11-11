from pathlib import Path
import os

from crawler.crawler_services.helper_services.env_handler import env_handler
S_SERVER = env_handler.get_instance().env('S_SERVER')

class RAW_PATH_CONSTANTS:
  S_SIGWIN_PATH = str(Path(__file__).parent.parent.parent.parent.parent) + "/cygwin64/bin/bash.exe --login"
  S_PROJECT_PATH = str(Path(__file__).parent.parent.parent)
  LOG_DIRECTORY = os.path.join(os.getcwd(), 'logs')
  UNIQUE_CRAWL_DIRECTORY = os.path.join(os.getcwd()+"/raw", 'unique_host')
  MODEL = "./raw/model/"


class NETWORK_MONITOR:
  S_PING_URL = "https://duckduckgo.com"


class LOG_CONSTANTS:
  S_LOGS_KEY = "70be40974f068bb7abd5b441b0b8386b"


class TOR_CONSTANTS:
  S_SHELL_CONFIG_PATH = str(Path(__file__).parent.parent.parent) + "/crawler/crawler_services/raw/config_script.sh"
  S_TOR_PATH = str(Path(__file__).parent.parent.parent.parent) + "/tor_proxy"
  S_TOR_PROXY_PATH = S_TOR_PATH + "/9052"


class TOR_CONNECTION_CONSTANTS:
  S_TOR_CONNECTION_PORT = 9052
  S_TOR_CONTROL_PORT = 9053


class SPELL_CHECK_CONSTANTS:
  S_DICTIONARY_PATH = RAW_PATH_CONSTANTS.S_PROJECT_PATH + "/raw/dictionary/dictionary"
  S_DICTIONARY_MINI_PATH = RAW_PATH_CONSTANTS.S_PROJECT_PATH + "/raw/dictionary/dictionary_small"


class CLASSIFIER_CONSTANTS:
  S_CLASSIFIER_PICKLE_PATH = "/raw/classifier/web_classifier.sav"
  S_VECTORIZER_PATH = "/raw/classifier/class_vectorizer.csv"
  S_SELECTKBEST_PATH = "/raw/classifier/feature_vector.sav"
  S_IMAGE_CLASSIFIER_PATH = str(Path(__file__).parent.parent.parent) + "/libs/nudenet/.NudeNet/classifier_lite.onnx"


class CRAWL_SETTINGS_CONSTANTS:

  # Crawl Catagory
  S_THREAD_CATEGORY_GENERAL = "general"
  S_THREAD_CATEGORY_UNKNOWN = "unknown"
  S_THREAD_CATEGORY_ILLEGAL = "illegal"

  # Allowed Extentions
  S_DOC_TYPES = [
    '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
    '.odt', '.ods', '.odp', '.txt', '.rtf', '.csv', '.md', '.tex',
    '.epub', '.mobi', '.html', '.htm', '.xml', '.json', '.yaml', '.yml',
    '.log', '.pages', '.key', '.numbers',
    '.zip', '.tar', '.gz', '.rar', '.7z', '.bz2', '.xz', '.iso',
    '.dmg', '.tgz', '.tbz2', '.z', '.lz', '.lha', '.lzh',
    '.ps', '.eps', '.svg', '.odg', '.pub', '.wps', '.xps', '.pdfa', '.pdfx',
  ]

  # Local URL
  S_FEEDER_URL = f"{S_SERVER}/feeder"
  S_FEEDER_URL_UNIQUE = f"{S_SERVER}/feeder/unique"
  S_PARSERS_URL = f"{S_SERVER}/parser"
  S_PARSE_EXTRACTION_DIR = "raw/parsers"

  # Total Thread Instances Allowed
  S_UPDATE_STATUS_TIMEOUT = 1800
  S_UPDATE_PARSERS_TIMEOUT = 16400
  S_UPDATE_UNIQUE_FEEDER_TIMEOUT = 604800
  S_UPDATE_NETWORK_STATUS_TIMEOUT = 60
  S_UPDATE_STATUS_URL = "http://167.86.99.31/update_status/?pRequest=m_crawler"

  # Time Delay to Invoke New Url Requests
  S_TOR_NEW_CIRCUIT_INVOKE_DELAY = 1800

  # Max Allowed Depth
  S_MAX_ALLOWED_DEPTH = 1
  S_DEFAULT_DEPTH = 0

  # Max URL Timeout
  S_URL_TIMEOUT = 100
  S_HEADER_TIMEOUT = 30

  # User Agent
  S_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'

  # Max Thread Size
  S_LEAK_FILE_VERIFICATION_ALLOWED = False
  S_GENERIC_FILE_VERIFICATION_ALLOWED = False

  # Max URL Size
  S_MAX_URL_SIZE = 480

  # Unique Crawl
  S_ALLOW_UNIQUE_FEEDER_UPDATES = False

