from pydantic import BaseModel, Field
from typing import List, Set
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model

class leak_data_model(BaseModel):
    cards_data: List[card_extraction_model] = Field(default_factory=list)
    contact_link: str
    base_url: str
    false_positive_count: bool
