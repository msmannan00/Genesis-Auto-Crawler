from transformers import pipeline

# Load the zero-shot classification pipeline from the local path
model_path = "./raw/toxic_model/saved_model"
classifier = pipeline("zero-shot-classification", model=model_path, tokenizer=model_path, device=-1)

# Define a sample text for testing
text = "erotica"

# Define detailed candidate labels
candidate_labels = [
    # Cryptocurrency and Financial Services
    "cryptocurrency wallets and storage", "cryptocurrency exchanges and trading", "cryptocurrency mining services",
    "anonymous financial services", "financial fraud and scams", "investment fraud and schemes",

    # Marketplaces and E-commerce
    "general marketplaces for goods and services", "drug marketplaces", "weapons and firearms marketplaces",
    "stolen data and identity marketplaces", "counterfeit goods and fake documents", "hacking tools and exploit services",
    "digital products and services", "illegal software and licenses",

    # Privacy and Security
    "privacy tools and anonymity services", "encrypted messaging and communication", "darknet security forums and guides",
    "anonymity and privacy tutorials", "VPN and proxy services", "secure email and communication services",

    # Forums and Social Platforms
    "general discussion forums", "technology and hacking discussion forums", "whistleblower and leak platforms",
    "political discussion and activism forums", "conspiracy theory forums", "extremist and controversial forums",

    # Drugs and Controlled Substances
    "drug information and resources", "drug and substance marketplaces", "harm reduction and drug safety",

    # Weapons and Ammunition
    "firearms and weapons sales", "ammunition and explosives information", "DIY weapon and bomb-making guides",

    # Personal Identification Information (PII) and Stolen Data
    "personal identification information (PII) dumps", "password leaks and credential dumps", "credit card and financial data dumps",
    "identity theft and fraud services",

    # Illicit Services
    "fraud and carding services", "hacking and cyberattack services", "DDoS for hire and botnet rentals",
    "ransomware and malware services", "forged documents and identity services",

    # Educational and Research Resources
    "hacking and technical guides", "security vulnerability research", "anonymity and privacy research papers",
    "cryptocurrency guides and tutorials",

    # Legal and News Resources
    "darknet news and updates", "legal services for darknet users", "human rights and advocacy", "activism and social justice content",

    # Adult Content and Explicit Services
    "adult content and pornography", "escort and sex work services", "adult discussion forums",

    # Miscellaneous / Unclassified
    "miscellaneous content", "unknown or unclassified"
]

# Mapping of detailed labels to the 8 final categories
label_mapping = {
    # dataleaks
    "stolen data and identity marketplaces": "dataleaks",
    "personal identification information (PII) dumps": "dataleaks",
    "password leaks and credential dumps": "dataleaks",
    "credit card and financial data dumps": "dataleaks",
    "identity theft and fraud services": "dataleaks",

    # news
    "darknet news and updates": "news",
    "human rights and advocacy": "news",
    "legal services for darknet users": "news",
    "activism and social justice content": "news",

    # adult
    "adult content and pornography": "adult",
    "escort and sex work services": "adult",
    "adult discussion forums": "adult",

    # marketplace
    "general marketplaces for goods and services": "marketplace",
    "drug marketplaces": "marketplace",
    "weapons and firearms marketplaces": "marketplace",
    "counterfeit goods and fake documents": "marketplace",
    "hacking tools and exploit services": "marketplace",
    "digital products and services": "marketplace",
    "illegal software and licenses": "marketplace",

    # financial
    "cryptocurrency wallets and storage": "financial",
    "cryptocurrency exchanges and trading": "financial",
    "cryptocurrency mining services": "financial",
    "anonymous financial services": "financial",
    "financial fraud and scams": "financial",
    "investment fraud and schemes": "financial",

    # social forums
    "general discussion forums": "social forums",
    "technology and hacking discussion forums": "social forums",
    "whistleblower and leak platforms": "social forums",
    "political discussion and activism forums": "social forums",
    "conspiracy theory forums": "social forums",
    "extremist and controversial forums": "social forums",

    # Privacy and Security
    "privacy tools and anonymity services": "Privacy and Security",
    "encrypted messaging and communication": "Privacy and Security",
    "darknet security forums and guides": "Privacy and Security",
    "anonymity and privacy tutorials": "Privacy and Security",
    "VPN and proxy services": "Privacy and Security",
    "secure email and communication services": "Privacy and Security",
    "hacking and technical guides": "Privacy and Security",
    "security vulnerability research": "Privacy and Security",
    "anonymity and privacy research papers": "Privacy and Security",
    "cryptocurrency guides and tutorials": "Privacy and Security",

    # Miscellaneous
    "miscellaneous content": "Miscellaneous",
    "unknown or unclassified": "Miscellaneous"
}

# Run the classification
result = classifier(text, candidate_labels=candidate_labels, multi_label=True)

# Aggregate scores for each final category
final_scores = {category: 0.0 for category in set(label_mapping.values())}

# Sum the scores for each main category based on label mapping
for label, score in zip(result['labels'], result['scores']):
    if label in label_mapping:
        mapped_category = label_mapping[label]
        final_scores[mapped_category] += score

# Sort the final scores to get the top categories
sorted_final_scores = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

print("Prediction result:", sorted_final_scores)
