from typing import Literal

from pydantic import BaseModel, constr


class Request(BaseModel):
    message_id: constr(min_length=1)
    chat_id: constr(min_length=1)
    text: constr(min_length=1)
    message_sender: Literal["customer", "employee"]


class NewMessageRequest(BaseModel):
    event_type: constr(min_length=1) = "new_message"
    chat_id: constr(min_length=1)
    text: constr(min_length=1)
