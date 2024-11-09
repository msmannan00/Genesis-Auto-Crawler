from fastapi import FastAPI, HTTPException
from docker.model.ClassifyRequestModel import ClassifyRequestModel
from docker.model.ParseRequestModel import ParseRequestModel
from docker.nlp_manager.nlp_controller import nlp_controller
from docker.nlp_manager.nlp_enums import NLP_REQUEST_COMMANDS
from docker.topic_manager.topic_classifier_controller import topic_classifier_controller
from docker.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_COMMANDS, TOPIC_CATEGORIES
from queue import Queue, Empty
import threading
import logging
import traceback
from fastapi.testclient import TestClient
import asyncio

logging.basicConfig(level=logging.INFO)

class APIService:
    def __init__(self):
        self.app = FastAPI()
        self.nlp_controller_instance = nlp_controller()
        self.topic_classifier_instance = topic_classifier_controller()
        self.nlp_queue = Queue()
        self.topic_classifier_queue = Queue()
        self.app.add_api_route("/nlp/parse", self.nlp_parse, methods=["POST"])
        self.app.add_api_route("/hello", self.hello_world, methods=["GET"])
        self.app.add_api_route("/topic_classifier/predict", self.topic_classifier_predict, methods=["POST"])

        threading.Thread(target=self.process_nlp_requests, daemon=True).start()
        threading.Thread(target=self.process_topic_classifier_requests, daemon=True).start()

    def process_nlp_requests(self):
        while True:
            try:
                request, response_queue = self.nlp_queue.get(timeout=1)
                try:
                    result = self.nlp_controller_instance.invoke_trigger(NLP_REQUEST_COMMANDS.S_PARSE, [request.text])
                    if result is None:
                        raise Exception("Parsing returned None")
                    response_queue.put(result)
                except Exception as e:
                    logging.error(f"NLP processing error: {e}")
                    logging.error(traceback.format_exc())
                    response_queue.put({
                        "names": [],
                        "phone_numbers": [],
                        "emails": []
                    })
                finally:
                    # Ensure task_done is called only if get() was successful
                    self.nlp_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                logging.error(f"Unexpected error in NLP worker: {e}")
                logging.error(traceback.format_exc())

    def process_topic_classifier_requests(self):
        while True:
            try:
                request, response_queue = self.topic_classifier_queue.get(timeout=1)
                try:
                    result = self.topic_classifier_instance.invoke_trigger(
                        TOPIC_CLASSFIER_COMMANDS.S_PREDICT_CLASSIFIER,
                        [request.title, request.description, request.keyword]
                    )
                    if result is None:
                        raise Exception("Prediction returned None")
                    response_queue.put(result)
                except Exception as e:
                    logging.error(f"Topic classifier processing error: {e}")
                    logging.error(traceback.format_exc())
                    response_queue.put(TOPIC_CATEGORIES.S_THREAD_CATEGORY_GENERAL)
                finally:
                    # Ensure task_done is called only if get() was successful
                    self.topic_classifier_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                logging.error(f"Unexpected error in Topic Classifier worker: {e}")
                logging.error(traceback.format_exc())

    async def nlp_parse(self, request: ParseRequestModel):
        response_queue = Queue()
        self.nlp_queue.put((request, response_queue))
        result = response_queue.get()
        if isinstance(result, HTTPException):
            raise result
        return {"result": result}

    async def hello_world(self):
        return {"result": "Hello, World!"}

    async def topic_classifier_predict(self, request: ClassifyRequestModel):
        response_queue = Queue()
        self.topic_classifier_queue.put((request, response_queue))
        result = response_queue.get()
        if isinstance(result, HTTPException):
            raise result
        return {"result": result}

api_service = APIService()
app = api_service.app

# Testing code at the end
client = TestClient(app)

# Synchronous test for hello world
response = client.get("/hello")
print("Hello World Response:", response.json())

# Asynchronous test for NLP Parse and Topic Classifier Predict
async def test_api_endpoints():
    # Mock data for ParseRequestModel
    parse_request_data = {
        "text": "John Doe, contact me at john.doe@example.com or call me at +1234567890"
    }
    # Mock data for ClassifyRequestModel
    classify_request_data = {
        "title": "Sample title",
        "description": "Sample description",
        "keyword": "Sample keyword"
    }

    # Test /nlp/parse endpoint
    parse_response = client.post("/nlp/parse", json=parse_request_data)
    print("NLP Parse Response:", parse_response.json())

    # Test /topic_classifier/predict endpoint
    classify_response = client.post("/topic_classifier/predict", json=classify_request_data)
    print("Topic Classifier Predict Response:", classify_response.json())

# Run the asynchronous test
asyncio.run(test_api_endpoints())
