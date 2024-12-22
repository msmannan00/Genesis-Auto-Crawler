from pydantic import BaseModel
from typing import List

class index_model(BaseModel):
    m_base_url: str
    m_url: str
    m_network: str
    m_title: str
    m_meta_description: str
    m_content: str
    m_important_content: str
    m_images: List[str]
    m_sub_url: List[str]
    m_document: List[str]
    m_video: List[str]
    m_archive_url: List[str]
    m_validity_score: int
    m_meta_keywords: str
    m_content_type: List[str]
    m_section: List[str]
    m_names: List[str]
    m_emails: List[str]
    m_phone_numbers: List[str]
    m_clearnet_links: List[str]

def index_model_init(
    m_base_url: str,
    m_url: str,
    m_network: str,
    m_title: str,
    m_meta_description: str,
    m_content: str,
    m_important_content: str,
    m_images: List[str],
    m_document: List[str],
    m_sub_url: List[str],
    m_video: List[str],
    m_archive_url: List[str],
    m_validity_score: int,
    m_meta_keywords: str,
    m_content_type: List[str],
    m_section: List[str],
    m_names: List[str],
    m_emails: List[str],
    m_phone_numbers: List[str],
    m_clearnet_links: List[str],
) -> index_model:
    return index_model(
        m_base_url=m_base_url,
        m_url=m_url,
        m_network=m_network,
        m_title=m_title,
        m_meta_description=m_meta_description,
        m_content=m_content,
        m_important_content=m_important_content,
        m_images=m_images,
        m_document=m_document,
        m_video=m_video,
        m_archive_url=m_archive_url,
        m_sub_url= m_sub_url,
        m_validity_score=m_validity_score,
        m_meta_keywords=m_meta_keywords,
        m_content_type=m_content_type,
        m_section=m_section,
        m_names=m_names,
        m_emails=m_emails,
        m_phone_numbers=m_phone_numbers,
        m_clearnet_links=m_clearnet_links,
    )
