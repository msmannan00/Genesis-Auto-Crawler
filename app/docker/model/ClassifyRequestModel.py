from pydantic import BaseModel


class ClassifyRequestModel(BaseModel):
    title: str
    description: str
    keyword: str