from dataclasses import dataclass, field
from typing import List, Optional

from crawler.constants.enums import VALID_NETWORK_TYPES, VALID_CONTENT_TYPES

@dataclass
class card_extraction_model:
    m_title: str
    m_url: str
    m_base_url: str
    m_content: str
    m_important_content: str
    m_network: str
    m_content_type: List[str] = field(default_factory=list)
    m_weblink: List[str] = field(default_factory=list)
    m_dumplink: List[str] = field(default_factory=list)
    m_name: str = ""
    m_email_addresses: List[str] = field(default_factory=list)
    m_industry: Optional[str] = None
    m_phone_numbers: List[str] = field(default_factory=list)
    m_addresses: List[str] = field(default_factory=list)
    m_social_media_profiles: List[str] = field(default_factory=list)
    m_websites: List[str] = field(default_factory=list)
    m_company_name: Optional[str] = None
    m_logo_or_images: List[str] = field(default_factory=list)
    m_leak_date: Optional[str] = None
    m_data_size: Optional[str] = None
    m_country_name: Optional[str] = None
    m_revenue: Optional[str] = None

    def __post_init__(self):
        required_fields = ["m_title", "m_url", "m_content", "m_base_url", "m_important_content"]

        for field_name in required_fields:
            if getattr(self, field_name) is None:
                raise ValueError(f"The field '{field_name}' is required and cannot be None.")

        if self.m_network not in VALID_NETWORK_TYPES:
            raise ValueError(f"Invalid network type provided: {self.m_network}. Must be one of {', '.join(VALID_NETWORK_TYPES)}.")

        if not isinstance(self.m_content_type, list):
            raise ValueError("m_content_type must be a list of valid content types.")

        if not all(content in VALID_CONTENT_TYPES for content in self.m_content_type):
            raise ValueError(f"Invalid content type(s) provided: {self.m_content_type}. Must be a subset of {', '.join(VALID_CONTENT_TYPES)}.")
