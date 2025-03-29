# type: ignore
import datetime
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
    
class Period(BaseModel):
    id: int
    name: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    
class PeriodCollection(BaseCollectionModel[Period]): ...
    
class RequestError(Exception):
    status: int
    text: str | None
    
    def __init__(self, status: int, text: str | None):
        super().__init__(f"Request Error: \nStatus {status}\nResp: {text}")
        
class ScheduleUpdateEntry(BaseModel):
    class_id: int
    period: int
    teacher_id: int
    subject_id: int
    classroom_id: int | None
    block_id: int | None
    block_part_id: int | None
    profile_id: int | None
        
class ScheduleUpdateInfo(BaseModel):
    before: List[ScheduleUpdateEntry]
    now: List[ScheduleUpdateEntry]
    day: str
    period: str