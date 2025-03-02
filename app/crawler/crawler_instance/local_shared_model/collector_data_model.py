from pydantic import BaseModel, Field, SkipValidation
from typing import List
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model


class collector_data_model(BaseModel):
    cards_data: List[SkipValidation[card_extraction_model]] = Field(default_factory=list)
    base_url: str = ""
    m_network: str = ""
