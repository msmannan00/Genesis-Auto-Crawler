import gc
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from api.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_MODEL, TOPIC_CATEGORIES
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class topic_classifier_model:

    def __init__(self):
        self.local_model_dir = "./raw/model/topic_classifier"
        self.tokenizer = AutoTokenizer.from_pretrained(self.local_model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.local_model_dir)

    def __predict_classifier(self, p_title, p_description, p_keyword):
        input_text = p_title + p_description + p_keyword
        max_length = 512
        if len(input_text) > max_length:
            input_text = input_text[:max_length]
        if not input_text:
            return [TOPIC_CATEGORIES.S_THREAD_CATEGORY_GENERAL]

        inputs = self.tokenizer(input_text, return_tensors="pt", truncation=True, max_length=max_length)
        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits.squeeze()  # Remove batch dimension
        max_score = logits.max().item()
        threshold = max(0.4 * max_score, 2.0)

        top_k = 3
        top_k_values, top_k_indices = torch.topk(logits, k=logits.size(0), dim=-1)

        unique_predictions = []
        for idx, score in zip(top_k_indices.tolist(), top_k_values.tolist()):
            if len(unique_predictions) < top_k and score >= threshold:
                label = TOPIC_CATEGORIES.get_label(idx)
                if label not in unique_predictions:
                    unique_predictions.append(label)
            if len(unique_predictions) >= top_k:
                break

        return unique_predictions

    def cleanup(self):
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        self.tokenizer = None
        self.model = None
        gc.collect()

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == TOPIC_CLASSFIER_MODEL.S_PREDICT_CLASSIFIER:
            return self.__predict_classifier(p_data[0], p_data[1], p_data[2])
        if p_command == TOPIC_CLASSFIER_MODEL.S_CLEAN_CLASSIFIER:
            return self.cleanup()
