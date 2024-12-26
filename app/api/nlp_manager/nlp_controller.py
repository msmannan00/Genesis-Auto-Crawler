import re
import phonenumbers
from transformers import pipeline
from api.nlp_manager.nlp_enums import NLP_REQUEST_COMMANDS


class nlp_controller:

    def __init__(self):
        model_path = "./raw/model/info_classifier"
        self.ner_pipeline = pipeline("ner", model=model_path, tokenizer=model_path, aggregation_strategy="simple")

    def __parse(self, text):
        names = []

        phone_numbers = set(re.findall(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', text))
        emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))

        validated_phone_numbers = set()
        for phone in phone_numbers:
            phone_cleaned = re.sub(r'[^\d+]', '', phone)
            try:
                phone_obj = phonenumbers.parse(phone_cleaned, None)
                if phonenumbers.is_valid_number(phone_obj):
                    validated_phone_numbers.add(phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164))
            except phonenumbers.NumberParseException:
                continue

        result = {
            "names": list(names),
            "phone_numbers": list(validated_phone_numbers),
            "emails": list(emails)
        }
        return result

    def invoke_trigger(self, command, data=None):
        if command == NLP_REQUEST_COMMANDS.S_PARSE:
            return self.__parse(data[0])
