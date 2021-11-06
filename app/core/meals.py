"""Meals core."""


from enum import Enum
from typing import Any

from fastapi import Query
from pydantic import parse_obj_as


class SwapMode(Enum):
    """Valid swap modes."""

    ALL = "all"
    LUNCH = "lunch"
    LUNCH_1 = "lunch_1"
    LUNCH_2 = "lunch_2"
    DINNER = "dinner"


class OutputEnum(Enum):
    """Output types for meals."""

    SIMPLE = "simple"
    NORMAL = "normal"


def simplify_asked(output: OutputEnum = Query(None, description="Simplify output")):
    """Returns true if the output must be simplified."""
    return output == OutputEnum.SIMPLE


def paginate(skip: int = 0, limit: int = 100):
    """Returns the pagination."""
    return {"skip": skip, "limit": limit}


def simplify(input_data: Any, simplified_model: Any, simplify_flag: bool):
    """Simplifies output if needed."""
    if not simplify_flag:
        return input_data
    return parse_obj_as(simplified_model, input_data)


def swap_attrs(obj1: Any, obj2: Any, attrname: str):
    attr1 = getattr(obj1, attrname)
    attr2 = getattr(obj2, attrname)

    setattr(obj1, attrname, attr2)
    setattr(obj2, attrname, attr1)
