from abc import ABC, abstractmethod
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
    def parse_leak_data(self, html_content: str, p_data_url: str) -> collector_data_model:
        """Parse leak data from HTML content and return a tuple of collector_data_model and a set of sub-links."""
        pass
