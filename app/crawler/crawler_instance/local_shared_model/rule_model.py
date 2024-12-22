from enum import Enum

class FetchConfig(str, Enum):
    SELENIUM = "selenium"
    REQUESTS = "requests"

class FetchProxy(str, Enum):
    TOR = "tor"
    NONE = "none"

class RuleModel:
    def __init__(self, m_depth: int = 2, m_sub_url_length = 50, m_fetch_config: FetchConfig = FetchConfig.SELENIUM, m_fetch_proxy: FetchProxy = FetchProxy.NONE):
        self.m_depth = m_depth
        self.m_fetch_config = m_fetch_config
        self.m_fetch_proxy = m_fetch_proxy
        self.m_sub_url_length = m_sub_url_length
