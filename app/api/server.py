import json
from typing import Optional, Dict

from fastapi import FastAPI, Query
from .model.ClassifyRequestModel import ClassifyRequestModel
from .model.ParseRequestModel import ParseRequestModel
from .nlp_manager.nlp_controller import nlp_controller
from .nlp_manager.nlp_enums import NLP_REQUEST_COMMANDS
from .runtime_parse_manager.runtime_parse_controller import runtime_parse_controller
from .topic_manager.topic_classifier_controller import topic_classifier_controller
from .topic_manager.topic_classifier_enums import TOPIC_CLASSFIER_COMMANDS, TOPIC_CATEGORIES
import asyncio
import logging
from fastapi import FastAPI, Query, Request

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class APIService:

    def __init__(self):
        self.app = FastAPI()
        self.m_runtime_parser = runtime_parse_controller()
        self.semaphore = asyncio.Semaphore(30)
        try:
            self.nlp_controller_instance = nlp_controller()
            self.topic_classifier_instance = topic_classifier_controller()
        except Exception as e:
            logger.critical("Failed to initialize controller instances.", exc_info=True)
            raise RuntimeError("Controller initialization failed") from e

        self.app.add_api_route("/nlp/parse", self.nlp_parse, methods=["POST"])
        self.app.add_api_route("/topic_classifier/predict", self.topic_classifier_predict, methods=["POST"])
        self.app.add_api_route("/runtime/parse", self.runtime_parse, methods=["POST"])

    async def runtime_parse(self, request: Request):
        payload = await request.json()
        query: Dict[str, str] = payload.get("query", {})

        print("Received payload:", payload, flush=True)
        print("Parsed query:", query, flush=True)

        if not query or all(value == "" for value in query.values()):
            return {"error": "No valid query parameters provided or all values are empty"}

        async with self.semaphore:
            response = await self.m_runtime_parser.get_email_username(query)

        return response

    async def process_request(self, request, command, controller, default_result, timeout=15):
        async with self.semaphore:
            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(controller, command, request),
                    timeout=timeout
                )
                return {"result": result}
            except asyncio.TimeoutError:
                logger.warning(f"Request for command '{command}' timed out after {timeout} seconds. Returning default result.")
                return {"result": default_result}
            except Exception:
                logger.error(f"An error occurred while processing request for command '{command}'. Returning default result.", exc_info=True)
                return {"result": default_result}

    async def nlp_parse(self, request: ParseRequestModel):
        logger.info("Received request at /nlp/parse")
        return await self.process_request(
            request=[request.text],
            command=NLP_REQUEST_COMMANDS.S_PARSE,
            controller=self.nlp_controller_instance.invoke_trigger,
            default_result={"names": [], "phone_numbers": [], "emails": []}
        )

    async def topic_classifier_predict(self, request: ClassifyRequestModel):
        logger.info("Received request at /topic_classifier/predict")
        return await self.process_request(
            request=[request.title, request.description, request.keyword],
            command=TOPIC_CLASSFIER_COMMANDS.S_PREDICT_CLASSIFIER,
            controller=self.topic_classifier_instance.invoke_trigger,
            default_result=TOPIC_CATEGORIES.S_THREAD_CATEGORY_GENERAL
        )

api_service = APIService()
app = api_service.app
