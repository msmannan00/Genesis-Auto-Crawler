from abc import ABC, abstractmethod
from typing import Dict
from playwright.async_api import BrowserContext
from crawler.crawler_instance.local_shared_model.collector_data_model import collector_data_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel

class collector_interface(ABC):
    @property
    @abstractmethod
    def base_url(self) -> str:
        """Return the base URL."""
        pass

    @property
    @abstractmethod
    def rule_config(self) -> RuleModel:
        """Return the rule configuration."""
        pass

    @abstractmethod

    def parse_leak_data(self, query: Dict[str, str], context: BrowserContext) -> collector_data_model:
        pass
