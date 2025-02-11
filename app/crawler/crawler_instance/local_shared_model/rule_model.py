from enum import Enum

class FetchConfig(str, Enum):
    SELENIUM = "selenium"
    REQUESTS = "requests"

class FetchProxy(str, Enum):
    TOR = "tor"
    NONE = "none"

class RuleModel:
    def __init__(self, m_timeout: int = 7200, m_fetch_config: FetchConfig = FetchConfig.SELENIUM, m_fetch_proxy = FetchProxy.NONE):
        self.m_timeout = m_timeout
        self.m_fetch_config = m_fetch_config
        self.m_fetch_proxy = m_fetch_proxy
