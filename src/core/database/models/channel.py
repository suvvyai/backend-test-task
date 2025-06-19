from beanie import Document, PydanticObjectId


class Channel(Document):
    chat_bot_id: PydanticObjectId
    chat_id: str
    response_url: str
    response_token: str
