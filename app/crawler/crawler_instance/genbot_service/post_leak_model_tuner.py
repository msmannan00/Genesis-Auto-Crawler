from typing import Set, List, Tuple
from crawler.crawler_instance.local_shared_model.leak_data_model import leak_data_model
from crawler.crawler_instance.local_shared_model.card_extraction_model import card_extraction_model


class post_leak_model_tuner:
  __instance = None

  def __init__(self):
    self.local_cards_data: List[card_extraction_model] = []
    self.local_sub_links: Set[str] = set()

  def process(self, data_model: leak_data_model, sub_links: Set[str]) -> Tuple[leak_data_model, Set[str]]:
    if data_model is not None:
      unique_cards = self.update_cards_data(data_model.cards_data)
      data_model.cards_data = unique_cards

    unique_sub_links = self.update_sub_links(sub_links)
    return data_model, unique_sub_links

  def update_cards_data(self, new_cards_data: List[card_extraction_model]) -> List[card_extraction_model]:
    existing_card_keys = set((card.m_title, tuple(card.m_url), tuple(card.m_content)) for card in self.local_cards_data)
    unique_new_cards = []

    for card_data in new_cards_data:
      unique_key = (card_data.m_title, card_data.m_url, card_data.m_content)
      if unique_key not in existing_card_keys:
        self.local_cards_data.append(card_data)
        unique_new_cards.append(card_data)
        existing_card_keys.add(unique_key)

    return unique_new_cards

  def update_sub_links(self, new_sub_links: Set[str]) -> Set[str]:
    unique_new_sub_links = new_sub_links - self.local_sub_links
    self.local_sub_links.update(unique_new_sub_links)
    return unique_new_sub_links
