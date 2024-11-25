# Local Imports
from api.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_MODEL, TOPIC_CLASSFIER_COMMANDS
from api.topic_manager.topic_classifier_model import topic_classifier_model

class topic_classifier_controller:

    __m_classifier = None

    def __init__(self):
        self.__m_classifier = topic_classifier_model()

    def __predict_classifier(self, p_title, p_description, p_keyword):
        return self.__m_classifier.invoke_trigger(TOPIC_CLASSFIER_MODEL.S_PREDICT_CLASSIFIER, [p_title, p_description, p_keyword])

    @classmethod
    def destroy_instance(cls):
        cls.__instance = None

    def __clean_classifier(self):
        self.__m_classifier.invoke_trigger(TOPIC_CLASSFIER_MODEL.S_CLEAN_CLASSIFIER)
        self.__m_classifier = None
        del self.__m_classifier

    def invoke_trigger(self, p_command, p_data=None):
        if p_command == TOPIC_CLASSFIER_COMMANDS.S_PREDICT_CLASSIFIER:
            return self.__predict_classifier(p_data[0], p_data[1], p_data[2])
        if p_command == TOPIC_CLASSFIER_COMMANDS.S_CLEAN_CLASSIFIER:
            return self.__clean_classifier()
