from abc import abstractmethod, ABC
from typing import Tuple, Set
from crawler.crawler_instance.local_shared_model.leak_data_model import leak_data_model
from crawler.crawler_instance.local_shared_model.rule_model import RuleModel


class leak_extractor_interface(ABC):
  @abstractmethod
  def parse_leak_data(self, html_content: str, p_data_url: str) -> Tuple[leak_data_model, Set[str]]:
    """Parse leak data from HTML content and return a tuple of leak_data_model and a set of sub-links."""
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

  @abstractmethod
  def contact_page(self) -> str:
    """Return the contact page URL as a string."""
    pass
