from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class card_extraction_model:
    m_title: str = ""
    m_url: str = ""
    m_content: str = ""
    m_base_url: str = ""
    m_important_content: str = ""
    m_content_type: str = "general"
    m_weblink: List[str] = field(default_factory=list)
    m_dumplink: List[str] = field(default_factory=list)
    m_extra_tags: List[str] = field(default_factory=list)
    m_sections: List[str] = field(default_factory=list)
    m_name: str = ""
    m_email_addresses: List[str] = field(default_factory=list)
    m_phone_numbers: List[str] = field(default_factory=list)
    m_addresses: List[str] = field(default_factory=list)
    m_social_media_profiles: List[str] = field(default_factory=list)
    m_websites: List[str] = field(default_factory=list)
    m_company_name: Optional[str] = None
    m_industry: Optional[str] = None
    m_job_title_or_position: Optional[str] = None
    m_associated_entities: List[str] = field(default_factory=list)
    m_aliases_or_alternate_names: List[str] = field(default_factory=list)
    m_logo_or_images: List[str] = field(default_factory=list)
    m_business_categories: List[str] = field(default_factory=list)
    m_services_or_products: List[str] = field(default_factory=list)
    m_public_records: List[str] = field(default_factory=list)
    m_online_activity: List[str] = field(default_factory=list)
    m_leak_date: Optional[str] = None
    m_last_updated: Optional[str] = None

