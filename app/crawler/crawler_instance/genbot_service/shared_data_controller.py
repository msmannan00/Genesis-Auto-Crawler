import requests
from crawler.constants.app_status import APP_STATUS
from crawler.crawler_services.log_manager.log_controller import log


class shared_data_controller:
    __instance = None
    topic_classifier_model = None
    nlp_model = None
    api_base_url = "http://api:8000"
    _cache = {}

    def __init__(self):
        if shared_data_controller.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            shared_data_controller.__instance = self

    def init(self):
        if not APP_STATUS.DOCKERIZED_RUN:
            from api.nlp_manager.nlp_controller import nlp_controller
            from api.topic_manager.topic_classifier_controller import topic_classifier_controller
            self.nlp_model = nlp_controller()
            self.topic_classifier_model = topic_classifier_controller()

    def _request(self, endpoint, method="POST", payload=None):
        url = f"{self.api_base_url}/{endpoint}"
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=payload)
            elif method.upper() == "GET":
                response = requests.get(url, params=payload)
            else:
                raise ValueError("Unsupported HTTP method")
            response.raise_for_status()
            return response.json()
        except Exception as ex:
            log.g().i(ex)

    def trigger_topic_classifier(self, p_base_url, p_title, p_important_content, p_content):
        if p_base_url in self._cache:
            return self._cache[p_base_url]

        if APP_STATUS.DOCKERIZED_RUN:
            payload = {"title": p_title, "description": p_important_content, "keyword": p_content}
            result = self._request("topic_classifier/predict", method="POST", payload=payload).get("result")
        else:
            from api.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_COMMANDS
            result = self.topic_classifier_model.invoke_trigger(TOPIC_CLASSFIER_COMMANDS.S_PREDICT_CLASSIFIER, [p_title, p_important_content, p_content])

        self._cache[p_base_url] = result
        return result

    def trigger_nlp_classifier(self, p_text):
        if APP_STATUS.DOCKERIZED_RUN:
            payload = {"text": p_text}
            result = self._request("nlp/parse", method="POST", payload=payload).get("result")
        else:
            from api.nlp_manager import NLP_REQUEST_COMMANDS
            result = self.nlp_model.invoke_trigger(NLP_REQUEST_COMMANDS.S_PARSE, [p_text])

        return result

    @staticmethod
    def get_instance():
        if shared_data_controller.__instance is None:
            shared_data_controller()
        return shared_data_controller.__instance
