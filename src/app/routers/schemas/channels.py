from beanie import PydanticObjectId
from pydantic import BaseModel, constr


class CreateRequest(BaseModel):
    chat_id: constr(min_length=1)
    response_url: constr(min_length=1)
    response_token: constr(min_length=1)


class Response(BaseModel):
    id: PydanticObjectId
    chat_id: str
    chat_bot_id: PydanticObjectId
    response_url: str
    response_token: str

    class Config:
        from_attributes = True
