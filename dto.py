from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Error(BaseModel):
    code: int
    message: str


class SendPlaceInfoResponse(BaseModel):
    chat_id: str
    message_id: str


class SendPlaceInfoRequestWithMessage(BaseModel):
    user_id: str
    place: SendPlaceInfoResponse
    date_time: str


class SendPlaceInfoRequest(BaseModel):
    chat_id: str


class Command(BaseModel):
    user_id: str
    place: SendPlaceInfoRequest
    name: str
    date_time: str


class EnterKeyboard(BaseModel):
    user_id: str
    button: str
    place: SendPlaceInfoResponse
    date_time: str



class Message(BaseModel):
    user_id: str
    place: SendPlaceInfoRequest
    text: str


class EnterButtonKeyboard(BaseModel):
    send_place_info: SendPlaceInfoResponse


class Button(BaseModel):
    text: str


class KeyboardResponse(BaseModel):
    user_id: str
    place: SendPlaceInfoResponse
    date_time: str


class KeyboardRequestUpdate(BaseModel):
    user_id: str
    place: SendPlaceInfoRequestWithMessage
    title: str
    buttons: List[Button]


class KeyboardRequest(BaseModel):
    user_id: str
    place: SendPlaceInfoRequest
    title: str
    buttons: List[Button]


class Image(BaseModel):
    attachments_base64: List[str] = []
    user_id: Optional[str] = None
    place: Optional[SendPlaceInfoRequest] = None
    date_time: Optional[str] = None


class ActionOnMessage(BaseModel):
    user_id: str
    place: SendPlaceInfoRequest
    action: str
    date_time: str


class ImageURL(BaseModel):
    attachment_urls: List[str]

