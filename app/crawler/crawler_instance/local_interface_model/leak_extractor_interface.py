from abc import abstractmethod, ABC
from typing import List

from playwright.async_api import Page

from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model
from crawler.crawler_instance.local_shared_model.leak_data_model import leak_data_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel
from crawler.crawler_services.redis_manager.redis_enums import REDIS_COMMANDS, CUSTOM_SCRIPT_REDIS_KEYS


class leak_extractor_interface(ABC):
    @abstractmethod
    def parse_leak_data(self, page:Page) -> leak_data_model:
        """Parse leak data from HTML content and return a tuple of leak_data_model and a set of sub-links."""
        pass

    @property
    @abstractmethod
    def seed_url(self) -> str:
        """Return the base URL."""
        pass

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

    @property
    @abstractmethod
    def card_data(self) -> List[card_extraction_model]:
        """Return the rule configuration."""
        pass

    @abstractmethod
    def contact_page(self) -> str:
        """Return the contact page URL as a string."""
        pass

    @abstractmethod
    def invoke_db(self, command:REDIS_COMMANDS, key: CUSTOM_SCRIPT_REDIS_KEYS, value) -> None:
        """Set data or get data from Redis for a given key and value."""
        pass