import re


class PhoneNumberExtractor:
  @staticmethod
  def extract_phone_numbers(text: str) -> list:
    phone_pattern = r'\(?\b\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b'
    phone_numbers = re.findall(phone_pattern, text)

    filtered_phone_numbers = []
    for number in phone_numbers:
      digits_only = re.sub(r'[^0-9]', '', number)

      if 7 <= len(digits_only) <= 15:
        if '(' in text[text.find(number):text.find(number) + len(number)]:
          filtered_phone_numbers.append(number)
        else:
          filtered_phone_numbers.append(number)

    return filtered_phone_numbers

# Example usage
text = """
School District of Colfax is a company that operates in the Education industry. It employs 51-100 people and has $10M-$25M of revenue.

Phone Number (715) 962-3155

Revenue $14.7 Million
"""

extractor = PhoneNumberExtractor()
phone_numbers = extractor.extract_phone_numbers(text)
print(phone_numbers)