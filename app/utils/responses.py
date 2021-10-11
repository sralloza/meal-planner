from typing import Dict, List, Tuple, Union

from pydantic import BaseModel


class Message(BaseModel):
    detail: str


class ErrorMessage(Message):
    class Config:
        schema_extra = {"example": {"detail": "error explanation"}}


class Version(BaseModel):
    version: str

    class Config:
        schema_extra = {"example": {"version": "1.0.0"}}


def gen_responses(
    responses: Dict[int, Union[str, Tuple[str, BaseModel]]], ignore: List[int] = None
):
    ignore = ignore or list()
    data = {}

    for code, reason in responses.items():
        if isinstance(reason, tuple):
            reason, model = reason
        else:
            model = ErrorMessage

        data[code] = {"description": reason}
        if code not in ignore:  # noqa
            data[code]["model"] = model

    return {"responses": data}
