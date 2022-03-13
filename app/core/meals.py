"""Meals core."""


from enum import Enum
from typing import Any, List

from fastapi import Query
from pydantic import parse_obj_as

from ..models.meal import Meal
from ..utils.misc import lowercase
from .config import settings

NULL_MAP = {
    "lunch1": settings.NULL_STR,
    "lunch1_frozen": False,
    "lunch2": None,
    "lunch2_frozen": False,
    "dinner": settings.NULL_STR,
    "dinner_frozen": False,
}


class SwapMode(Enum):
    """Valid swap modes."""

    ALL = "all"
    LUNCH = "lunch"
    LUNCH_1 = "lunch1"
    LUNCH_2 = "lunch2"
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


def set_attrs(old: Any, new: Any, attrnames: List[str]):
    for attr in attrnames:
        setattr(new, attr, getattr(old, attr))


def can_override_meal_from_shift(meal: Meal, attrnames: List[str]) -> bool:
    """Checks if the meal has all the attrs to null.

    A meal can be shifted (override some attrs from other meal) if all
    attrnames are considered null.
    """

    var_str = lowercase(settings.VARIABLE_STR)

    for attrname in attrnames:
        attr = lowercase(getattr(meal, attrname))
        null_str = lowercase(NULL_MAP[attrname])
        null_str = null_str.lower() if isinstance(null_str, str) else null_str

        if attr not in (null_str, var_str):
            return False
    return True
