"""Meals CRUD operations."""

from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func
from sqlalchemy.orm.session import Session

from ..crud.base import CRUDBase
from ..models import Meal
from ..schemas.meal import MealCreate, MealUpdate
from ..utils.misc import get_current_week


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
            self.raise_not_found_error(id=datetime.now().date())
        return meal_db

    def get_tomorrow_or_404(self, db: Session):
        """Get tomorrow's menu or return 404."""
        meal_db = self.get_tomorrow(db)
        if not meal_db:
            self.raise_not_found_error(id=self.get_tomorrow_date)
        return meal_db

    @staticmethod
    def get_tomorrow_date():
        """Returns tomorrow's date."""
        return (datetime.now() + timedelta(days=1)).date()

    def get_by_date_delta(self, db: Session, *, delta_days: int):
        """Get menu using a relative time delta."""
        date = (datetime.now() + timedelta(days=delta_days)).date()
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
