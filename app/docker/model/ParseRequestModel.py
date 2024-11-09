from pydantic import BaseModel


class ParseRequestModel(BaseModel):
    text: str