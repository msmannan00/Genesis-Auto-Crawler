import platform
import re
import subprocess
import sys
import phonenumbers
from gensim.parsing.preprocessing import STOPWORDS
from docker.nlp_manager.nlp_enums import NLP_REQUEST_COMMANDS

class nlp_controller:

  def __init__(self):
      try:
          import spacy
          self.nlp_core = spacy.load("en_core_web_sm")
      except OSError:
          print("Model not found. Downloading...")
          download_command = [sys.executable, "-m", "spacy", "download", "en_core_web_sm"]
          if platform.system().lower() == "windows":
              subprocess.run(download_command, shell=True, check=True)
          else:
              subprocess.run(download_command, check=True)

  def is_stop_word(self, p_word):
      return p_word in STOPWORDS

  def __parse(self, text):
      names = set()
      phone_numbers = set()
      emails = set()
      doc = self.nlp_core(text)

      for ent in doc.ents:
          if ent.label_ in {'PERSON', 'GPE', 'ORG'}:
              entity_text = ent.text.strip()
              if entity_text.replace(" ", "").isalpha():
                  if len(entity_text.split()) > 3:
                      for token in ent:
                          if token.pos_ == 'PROPN' and not self.is_stop_word(token.text):
                              names.add(token.text)
                  else:
                      if all(not self.is_stop_word(token.text) for token in ent):
                          names.add(entity_text)

      phone_matches = re.findall(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', text)
      for phone in phone_matches:
          phone = re.sub(r'[^\d+]', '', phone)
          try:
              phone_obj = phonenumbers.parse(phone, None)
              if phonenumbers.is_valid_number(phone_obj):
                  phone_numbers.add(phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164))
          except phonenumbers.NumberParseException:
              continue

      email_matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
      emails.update(email_matches)
      result = {
          "names": list(names),
          "phone_numbers": list(phone_numbers),
          "emails": list(emails)
      }
      return result

  def invoke_trigger(self, p_commands, p_data=None):
      if p_commands == NLP_REQUEST_COMMANDS.S_PARSE:
          return self.__parse(p_data[0])
