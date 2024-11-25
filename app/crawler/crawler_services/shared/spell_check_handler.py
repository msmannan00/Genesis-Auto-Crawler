# Local Imports
import logging
import re
import warnings
import nltk
from nltk import PorterStemmer
from crawler.constants.constant import SPELL_CHECK_CONSTANTS
from crawler.constants.strings import STRINGS
from crawler.crawler_services.shared.helper_method import helper_method
import os
import sys

warnings.filterwarnings("ignore")
logging.getLogger("nltk").setLevel(logging.CRITICAL)


def ensure_punkt_installed():
  try:
    nltk.data.find('tokenizers/punkt')
  except LookupError:
    with open(os.devnull, 'w') as fnull:
      sys.stdout = fnull
      sys.stderr = fnull
      try:
        nltk.download('punkt', quiet=True)
      finally:
        # Restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


ensure_punkt_installed()


class spell_checker_handler:
  __spell_check = None
  __m_porter_stemmer = None

  def __init__(self):
      self.__spell_check = set(open(SPELL_CHECK_CONSTANTS.S_DICTIONARY_PATH).read().split())
      self.__m_porter_stemmer = PorterStemmer()

  def init_dict(self):
    self.__spell_check = set(open(SPELL_CHECK_CONSTANTS.S_DICTIONARY_MINI_PATH).read().split())

  def validate_word(self, p_word):
    if p_word in self.__spell_check:
      return True
    else:
      return False

  def clean_sentence(self, p_text):
    m_text = re.sub('[^A-Za-z0-9]+', ' ', p_text)
    m_token_list = nltk.sent_tokenize(m_text)
    m_text_cleaned = STRINGS.S_EMPTY

    for m_token in m_token_list:
      if not helper_method.is_stop_word(m_token) and self.validate_word(m_token):
        m_text_cleaned += " " + m_token

    return m_text_cleaned

  def clean_paragraph(self, p_text):
    sentences = nltk.sent_tokenize(p_text)
    cleaned_sentences = STRINGS.S_EMPTY
    for sentence in sentences:
      p_sentence = sentence.lower()
      m_valid_count = 0
      m_invalid_count = 0
      m_tokenized_sentence = p_sentence.split()
      for m_token in m_tokenized_sentence:
        if helper_method.is_stop_word(m_token) is True or self.validate_word(m_token):
          m_valid_count += 1
        else:
          m_invalid_count += 1

      if m_valid_count > 0 and m_valid_count / (m_valid_count + m_invalid_count) >= 0.60:
        if len(cleaned_sentences) > 0:
          cleaned_sentences += " - " + sentence
        else:
          cleaned_sentences = sentence

    return cleaned_sentences
