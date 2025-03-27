# type: ignore
from pydantic import BaseModel
from pydantic_collections import BaseCollectionModel
from typing import Literal, List
    
class Subscription(BaseModel):
    receiver_id: int
    type: Literal["teacher", "class"]
    id: int

class Config(BaseModel):
    subscriptions: List[Subscription]
    
class Option(BaseModel):
    id: int
    name: str
    
class OptionCollection(BaseCollectionModel[Option]): ...
    
class RequestError(Exception):
    status: int
    text: str | None
    
    def __init__(self, status: int, text: str | None):
        super().__init__(f"Request Error: \nStatus {status}\nResp: {text}")