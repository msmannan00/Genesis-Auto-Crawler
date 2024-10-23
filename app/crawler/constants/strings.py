from crawler.constants.constant import TOR_CONNECTION_CONSTANTS


class STRINGS:
  S_EMPTY = ""
  S_EMPTY_SPACE = " "
  S_SEPERATOR = " : "
  S_UTF8_ENCODING = "utf-8"
  S_ONION_EXTENTION = ".onion"
  S_ISO = "unicode-escape"


class TOR_STRINGS:
  S_SOCKS_HTTP_PROXY = "socks5h://10.0.0.6:"
  S_SOCKS_HTTPS_PROXY = "socks5h://10.0.0.6:"
  S_RELEASE_PORT = 'for /f "tokens=5" %a in (\'netstat -aon ^| find "' + str(TOR_CONNECTION_CONSTANTS.S_TOR_CONNECTION_PORT) + '"\') do taskkill /f /pid %a'


class PARSE_STRINGS:
  S_CONTENT_LENGTH_HEADER = 'content-length'

class MANAGE_MESSAGES:
  S_APPLICATION_STARTING = "[0] Application starting"
  S_APPLICATION_ERROR = "[1] Application encountered an error"
  S_INSTALL_LIVE_URL_ERROR = "[2] Failed to install live URL"
  S_INSTALL_LIVE_URL_STARTED = "[3] Installation of live URL started"
  S_INSTALL_LIVE_URL_TIMEOUT = "[4] Installation of live URL timed out"
  S_REINIT_UNIQUE_URL = "[5] Reinitializing unique URL"
  S_LOAD_URL_ERROR = "[6] Error loading URL"
  S_FAILED_URL_ERROR = "[7] URL Fetching failed"
  S_GENBOT_ERROR = "[8] Genbot encountered an error"
  S_LOAD_URL_ERROR_MAIN = "[9] Error in main script while loading URL"
  S_SERVICE_NOT_INITIATED = "[10] Service not initiated"
  S_UNIQUE_INDEX_UPDATED_SUCCESSFULLY = "[11] Unique index updated successfully"
  S_UNIQUE_INDEX_UPDATE_FAILED = "[12] Failed to update unique index"
  S_UNIQUE_INDEX_FAILED = "[13] Unique index operation failed"
  S_WEB_REQUEST_PROCESSING_ERROR = "[14] Error processing web request from server"
  S_FILE_PARSED = "[15] File parsed successfully"
  S_LOW_YIELD_URL = "[16] Low yield URL detected"
  S_REINITIALIZING_CRAWLABLE_URL = "[17] Reinitializing crawlable URL"
  S_INSTALLED_URL = "[18] URL installed successfully"
  S_LOCAL_URL_PARSED = "[19] Local URL parsed successfully"
  S_UNIQUE_URL_CACHE_LOAD_FAILURE = "[20] Failed to load unique URL cache"
  S_ELASTIC_ERROR = "[21] Error executing elastic commands"
  S_SINGLETON_EXCEPTION = "[22] Singleton class violation"
  S_LOCAL_URL_PARSED_FAILED = "[23] Failed to parse local URL"
  S_LEAK_URL_PARSED_FAILED = "[24] Leak URL validation failed"
  S_INTERNET_CONNECTION_ISSUE = "[25] Internet connection issue detected"
  S_PARSING_STARTING = "[26] URL parsing started"
  S_DUPLICATE_CONTENT = "[27] Duplicate content detected"
  S_DUPLICATE_HOST_CONTENT = "[28] Duplicate host content detected"
  S_TOO_MANY_FAILURE = "[29] Too many failures, dropping host"
  S_DUPLICATE_HOST_HASH = "[30] Duplicate host hash detected"
  S_INSERT_FAILURE = "[31] Error occurred while inserting document"
  S_INSERT_SUCCESS = "[32] Document inserted successfully"
  S_UPDATE_FAILURE = "[33] Error occurred while updating document"
  S_UPDATE_SUCCESS = "[34] Document updated successfully"
  S_DELETE_FAILURE = "[35] Error occurred while deleting document"
  S_DELETE_SUCCESS = "[36] Document deleted successfully"
  S_READ_FAILURE = "[37] Error occurred while reading document"
  S_READ_SUCCESS = "[38] Document read successfully"
  S_COUNT_FAILURE = "[39] Error occurred while counting documents"
  S_REQUEST_FAILURE = "[40] Error occurred while sending request to elastic server"
  S_REQUEST_SUCCESS = "[41] Elastic server responded successfully"
  S_PARSER_LOAD_EXCEPTION = "[42] Parser loading exception occured"
  S_PARSER_LOAD_STARTED = "[43] Parser loading started"
  S_PARSER_LOAD_FINISHED = "[44] Parser loading finished"
  S_PARSING_WORKER_STARTED = "[45] URL parsing worker started"
  S_UNIQUE_PARSING_STARTED = "[46] Unique parsing started"
  S_UNIQUE_PARSING_URL_STARTED = "[47] Unique URL parsing URL started"
  S_UNIQUE_PARSING_URL_FINISHED = "[48] Unique URL parsing URL finished"
  S_UNIQUE_PARSING_PENDING = "[46] Unique parsing pending"
