from fastapi import FastAPI, HTTPException
from docker.model.ClassifyRequestModel import ClassifyRequestModel
from docker.model.ParseRequestModel import ParseRequestModel
from docker.nlp_manager.nlp_controller import nlp_controller
from docker.nlp_manager.nlp_enums import NLP_REQUEST_COMMANDS
from docker.topic_manager.topic_classifier_controller import topic_classifier_controller
from docker.topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_COMMANDS, TOPIC_CATEGORIES
from queue import Queue, Empty, Full
import threading
import logging
import traceback
import asyncio
import time
from concurrent.futures import TimeoutError as AsyncTimeoutError

logging.basicConfig(level=logging.INFO)


class APIService:
    def __init__(self):
        self.app = FastAPI()
        try:
            self.nlp_controller_instance = nlp_controller()
            self.topic_classifier_instance = topic_classifier_controller()
        except Exception as e:
            logging.critical(f"Failed to initialize controller instances: {e}")
            raise RuntimeError("Controller initialization failed") from e

        # Set max queue size to prevent overload
        self.nlp_queue = Queue(maxsize=1000)
        self.topic_classifier_queue = Queue(maxsize=1000)

        self.app.add_api_route("/nlp/parse", self.nlp_parse, methods=["POST"])
        self.app.add_api_route("/hello", self.hello_world, methods=["GET"])
        self.app.add_api_route("/topic_classifier/predict", self.topic_classifier_predict, methods=["POST"])

        try:
            threading.Thread(target=self.process_nlp_requests, daemon=True).start()
            threading.Thread(target=self.process_topic_classifier_requests, daemon=True).start()
        except Exception as e:
            logging.critical(f"Failed to start worker threads: {e}")
            raise RuntimeError("Worker threads startup failed") from e

    def process_nlp_requests(self):
        while True:
            try:
                request, response_queue = self.nlp_queue.get(timeout=1)
                try:
                    result = self.nlp_controller_instance.invoke_trigger(
                        NLP_REQUEST_COMMANDS.S_PARSE, [request.text]
                    )
                    if result is None:
                        raise ValueError("Parsing returned None")
                    response_queue.put(result)
                except Exception as e:
                    logging.error(f"NLP processing error: {e}")
                    logging.error(traceback.format_exc())
                    response_queue.put({"names": [], "phone_numbers": [], "emails": []})
                finally:
                    self.nlp_queue.task_done()
            except Empty:
                time.sleep(0.1)
            except Exception as e:
                logging.critical(f"Unexpected error in NLP worker: {e}")
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
                        raise ValueError("Prediction returned None")
                    response_queue.put(result)
                except Exception as e:
                    logging.error(f"Topic classifier processing error: {e}")
                    logging.error(traceback.format_exc())
                    response_queue.put(TOPIC_CATEGORIES.S_THREAD_CATEGORY_GENERAL)
                finally:
                    self.topic_classifier_queue.task_done()
            except Empty:
                time.sleep(0.1)
            except Exception as e:
                logging.critical(f"Unexpected error in Topic Classifier worker: {e}")
                logging.error(traceback.format_exc())

    async def nlp_parse(self, request: ParseRequestModel):
        response_queue = Queue()
        try:
            self.nlp_queue.put((request, response_queue), timeout=1)
        except Full:
            logging.error("NLP queue is full, rejecting request")
            raise HTTPException(status_code=503, detail="NLP service is overloaded")

        try:
            result = await asyncio.wait_for(self._get_response_from_queue(response_queue), timeout=5)
        except AsyncTimeoutError:
            logging.warning("NLP parse request timed out")
            result = {"names": [], "phone_numbers": [], "emails": []}
        except Exception as e:
            logging.error(f"Unexpected error in NLP parse: {e}")
            logging.error(traceback.format_exc())
            result = {"names": [], "phone_numbers": [], "emails": []}

        if isinstance(result, HTTPException):
            raise result
        return {"result": result}

    async def topic_classifier_predict(self, request: ClassifyRequestModel):
        response_queue = Queue()
        try:
            self.topic_classifier_queue.put((request, response_queue), timeout=1)
        except Full:
            logging.error("Topic classifier queue is full, rejecting request")
            raise HTTPException(status_code=503, detail="Topic classifier service is overloaded")

        try:
            result = await asyncio.wait_for(self._get_response_from_queue(response_queue), timeout=5)
        except AsyncTimeoutError:
            logging.warning("Topic classifier predict request timed out")
            result = TOPIC_CATEGORIES.S_THREAD_CATEGORY_GENERAL
        except Exception as e:
            logging.error(f"Unexpected error in topic classifier predict: {e}")
            logging.error(traceback.format_exc())
            result = TOPIC_CATEGORIES.S_THREAD_CATEGORY_GENERAL

        if isinstance(result, HTTPException):
            raise result
        return {"result": result}

    async def hello_world(self):
        return {"result": "Hello, World!"}

    async def _get_response_from_queue(self, response_queue: Queue):
        try:
            while True:
                try:
                    return response_queue.get_nowait()
                except Empty:
                    await asyncio.sleep(0.1)
        except Exception as e:
            logging.error(f"Error in queue response retrieval: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


api_service = APIService()
app = api_service.app
