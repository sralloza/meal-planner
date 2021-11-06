"""Meal schemas."""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from ..core.notion import create_notion_block


class MealId(BaseModel):
    id: date = Field(alias="date")


class BaseSimpleMeal(BaseModel):
    lunch1: str
    lunch2: Optional[str]
    dinner: str

    class Config:
        orm_mode = True
        extra = "forbid"


class BaseMeal(BaseSimpleMeal):
    lunch1_frozen: bool = False
    lunch2_frozen: bool = False
    dinner_frozen: bool = False

    @property
    def frozen(self) -> List[str]:
        out = []
        if self.lunch1_frozen:
            out.append(f"{self.lunch1.lower()} (C1)")
        if self.lunch2_frozen and self.lunch2:
            out.append(f"{self.lunch2.lower()} (C2)")
        if self.dinner_frozen:
            out.append(f"{self.dinner.lower()} (D)")
        return out

    def to_notion_blocks(self):
        blocks = []

        # Little alias for code reading
        _cnb = create_notion_block

        if self.lunch1:
            blocks.append(_cnb("  - Comida: "))
            blocks.append(_cnb(self.lunch1.lower(), code=self.lunch1_frozen))
            if self.lunch2:
                blocks.append(_cnb(" y "))
                blocks.append(_cnb(self.lunch2.lower(), code=self.lunch2_frozen))

        if self.dinner:
            if blocks:
                blocks.append(_cnb("\n"))
            blocks.append(_cnb("  - Cena: "))
            blocks.append(_cnb(self.dinner.lower(), code=self.dinner_frozen))

        return blocks


class Meal(BaseMeal, MealId):
    pass


class MealCreate(Meal):
    pass


class SimpleMeal(BaseSimpleMeal, MealId):
    pass


class MealUpdate(BaseMeal):
    lunch1: Optional[str]
    lunch1_frozen: Optional[bool]

    lunch2: Optional[str]
    lunch2_frozen: Optional[bool]

    dinner: Optional[str]
    dinner_frozen: Optional[bool]

    @validator("*")
    def check_invalid_none(cls, v, field):
        """Only lunch2 can be null."""
        if v is None:
            if field.name != "lunch2":
                raise ValueError(f"Field {field.name!r} can't be nullable")
        return v
