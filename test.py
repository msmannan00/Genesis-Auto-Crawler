import re
from transformers import pipeline
import phonenumbers

# Load the locally saved Hugging Face NER model and tokenizer
model_path = "./raw/model/info_classifier"
ner_pipeline = pipeline("ner", model=model_path, tokenizer=model_path, aggregation_strategy="simple")

# Sample text with misleading names and terms
text = """
    Abdul Mannan from OpenAI in California, Bitcoin City, and Etherium Valley is a renowned figure in blockchain.
    Contact him via john.doe@example.com or at +1-800-555-1234. Jane Smith, based at Blockchain House, can also be reached at +44 20 7946 0958.
    To learn more, email info@openai.com or call the support line at +1-123-456-7890.

    Other team members include Satoshi Nakamoto, the legend behind Bitcoin, and Vitalik Buterin, the founder of Etherium.
    Monero Pioneer and Litecoin Lead are also key players in the team. Monero Freebsd is a developer working alongside Panda Miner.
    Reach Panda Miner at panda@example.com or call +33 1 23 45 67 89.

    Special guests include Binance Whale and Kraken Trader, frequent contributors to Blockchain Forum. 
    You can reach them at crypto.whale@binance.com and kraken.trader@cryptomail.com respectively.

    Location-based contacts:
    - "Ethereum Node" at Etherium Park, known for its blockchain events.
    - "Bitcoin Network" in Blockchain Street, a popular destination for crypto enthusiasts.

    For privacy-related inquiries, contact Privacy Coin or Shield Wallet, or reach out to alice.bob@privacycoin.com.
    Support from Fake Name and Code Monero is available at support@monerohelp.com. Alternatively, call +1-999-555-2222 for assistance.
"""

# Run the text through the NER pipeline to extract entities
entities = ner_pipeline(text)

# Extract names with a minimum length filter to avoid short misclassified words
names = [entity['word'] for entity in entities if entity['entity_group'] == 'PER' and len(entity['word']) > 3]

# Use regular expressions for phone numbers and emails
phone_numbers = set(re.findall(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', text))
emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))

# Format phone numbers using `phonenumbers` for validation
validated_phone_numbers = set()
for phone in phone_numbers:
    phone_cleaned = re.sub(r'[^\d+]', '', phone)
    try:
        phone_obj = phonenumbers.parse(phone_cleaned, None)
        if phonenumbers.is_valid_number(phone_obj):
            validated_phone_numbers.add(phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164))
    except phonenumbers.NumberParseException:
        continue

# Output results
print("Extracted Names:", names)
print("Extracted Phone Numbers:", list(validated_phone_numbers))
print("Extracted Emails:", list(emails))
