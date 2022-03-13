"""Meals CRUD operations."""

import datetime
from typing import List

from sqlalchemy import func
from sqlalchemy.orm.session import Session

from ..core.config import settings
from ..core.meals import SwapMode, set_attrs, swap_attrs
from ..crud.base import CRUDBase
from ..models import Meal
from ..schemas.meal import MealCreate, MealUpdate
from ..utils.misc import get_current_week, lowercase

NULL_MAP = {
    "lunch1": settings.NULL_STR,
    "lunch1_frozen": False,
    "lunch2": None,
    "lunch2_frozen": False,
    "dinner": settings.NULL_STR,
    "dinner_frozen": False,
}


class CRUDMeal(CRUDBase[Meal, MealCreate, MealUpdate]):
    """Meal CRUD operations."""

    def create_multiple(self, db: Session, *, obj_in: List[MealCreate]) -> List[Meal]:
        """Create multiple meals."""
        out = []
        for obj in obj_in:
            out.append(self.create(db, obj_in=obj, commit_refresh=False))

        db.commit()
        for obj in out:
            db.refresh(obj)
        return out

    def get_today_or_404(self, db: Session):
        """Get today's menu or return 404."""
        meal_db = self.get_today(db)
        if not meal_db:
            self.raise_not_found_error(id=datetime.datetime.now().date())
        return meal_db

    def get_tomorrow_or_404(self, db: Session):
        """Get tomorrow's menu or return 404."""
        meal_db = self.get_tomorrow(db)
        if not meal_db:
            self.raise_not_found_error(id=self.get_tomorrow_date())
        return meal_db

    @staticmethod
    def get_tomorrow_date():
        """Returns tomorrow's date."""
        return (datetime.datetime.now() + datetime.timedelta(days=1)).date()

    def get_by_date_delta(self, db: Session, *, delta_days: int):
        """Get menu using a relative time delta."""
        date = (datetime.datetime.now() + datetime.timedelta(days=delta_days)).date()
        return self.get(db, id=date)

    def get_today(self, db: Session):
        """Get today's menu."""
        return self.get_by_date_delta(db, delta_days=0)

    def get_tomorrow(self, db: Session):
        """Get tomorrow's menu."""
        return self.get_by_date_delta(db, delta_days=1)

    def get_day_after_tomorrow(self, db: Session):
        """Get the day after tomorrow's menu."""
        return self.get_by_date_delta(db, delta_days=2)

    def get_week(self, db: Session, *, week: int):
        """Get week's menu."""
        return db.query(self.model).filter(func.weekofyear(self.model.id) == week).all()

    def get_week_delta(self, db: Session, *, delta_weeks: int):
        """Get week's menu using a relative time delta."""
        week = get_current_week() + delta_weeks
        return self.get_week(db, week=week)

    def get_current_week(self, db: Session):
        """Get current week's menu."""
        week = get_current_week()
        return self.get_week(db, week=week)

    def swap(
        self,
        db: Session,
        *,
        date_1: datetime.date,
        date_2: datetime.date,
        mode: SwapMode,
    ) -> List[Meal]:
        """Swaps two meals data."""
        obj1 = self.get_or_404(db, id=date_1)
        obj2 = self.get_or_404(db, id=date_2)

        attrnames = self.get_attrnames_from_swapmode(mode)
        for attr in attrnames:
            swap_attrs(obj1, obj2, attr)

        db.add(obj1)
        db.add(obj2)
        db.commit()
        db.refresh(obj1)
        db.refresh(obj2)

        return [obj1, obj2]

    @staticmethod
    def get_attrnames_from_swapmode(mode: SwapMode) -> List[str]:
        """Returns the attributes that must be edited for each SwapMode."""
        attrnames = []
        if mode == SwapMode.ALL:
            attrnames += ["lunch1", "lunch2", "dinner"]
        elif mode == SwapMode.LUNCH:
            attrnames += ["lunch1", "lunch2"]
        elif mode == SwapMode.LUNCH_1:
            attrnames.append("lunch1")
        elif mode == SwapMode.LUNCH_2:
            attrnames.append("lunch2")
        elif mode == SwapMode.DINNER:
            attrnames.append("dinner")

        if "lunch1" in attrnames:
            attrnames.append("lunch1_frozen")
        if "lunch2" in attrnames:
            attrnames.append("lunch2_frozen")
        if "dinner" in attrnames:
            attrnames.append("dinner_frozen")

        return attrnames

    def shift(self, db: Session, *, date: datetime.date, mode: SwapMode):
        """Shifts all meals x days to the future."""
        meal_to_move = self.get(db, id=date)
        # If there is no meal for that date we don't have to do anything
        if meal_to_move is None:
            return []

        attrnames = self.get_attrnames_from_swapmode(mode)
        meals_to_edit = self.get_days_to_shift(db, meal_to_move, attrnames)

        for meal_to_edit in meals_to_edit:
            db.refresh(meal_to_edit)

        # Shift all meals
        meals_to_edit.sort(key=lambda x: x.id, reverse=True)
        for idx, meal_to_move in enumerate(meals_to_edit):
            if idx:
                set_attrs(meals_to_edit[idx], meals_to_edit[idx - 1], attrnames)

        # Remove attributes from first meal
        for attr in attrnames:
            setattr(meal_to_move, attr, NULL_MAP[attr])

        db.add_all(meals_to_edit)
        db.commit()

        meals_to_edit.sort(key=lambda x: x.id)
        return meals_to_edit

    def can_override_meal_from_shift(self, meal: Meal, attrnames: List[str]) -> bool:
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

    def get_days_to_shift(
        self, db: Session, first_meal: Meal, attrnames: List[str]
    ) -> List[Meal]:
        """Returns a list of meals to edit after shifting."""
        next_day_id = first_meal.id + datetime.timedelta(days=1)
        next_day_meal = self.get(db, id=next_day_id)
        if next_day_meal is None:
            new_meal = MealCreate(
                date=next_day_id, lunch1=settings.NULL_STR, dinner=settings.NULL_STR
            )
            next_day_meal = self.create(db, obj_in=new_meal)
            return [first_meal, next_day_meal]

        if self.can_override_meal_from_shift(next_day_meal, attrnames):
            return [first_meal, next_day_meal]

        return self.get_days_to_shift(db, next_day_meal, attrnames) + [first_meal]

    def remove_week(self, db: Session, *, week: int):
        """Remove meals for the entire week."""
        meals = self.get_week(db, week=week)
        for meal_db in meals:
            self.remove(db, id=meal_db.id)

    def remove_current_week(self, db: Session):
        """Remove current week's meals."""
        week = get_current_week()
        self.remove_week(db, week=week)


meal = CRUDMeal(Meal)
