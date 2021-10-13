from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func
from sqlalchemy.orm.session import Session

from ..crud.base import CRUDBase
from ..models import Meal
from ..schemas.meal import MealCreate, MealUpdate
from ..utils.misc import get_current_week


class CRUDMeal(CRUDBase[Meal, MealCreate, MealUpdate]):
    def create_multiple(self, db: Session, *, obj_in: List[MealCreate]) -> List[Meal]:
        out = []
        for obj in obj_in:
            out.append(self.create(db, obj_in=obj, commit_refresh=False))

        db.commit()
        for obj in out:
            db.refresh(obj)
        return out

    def get_today_or_404(self, db: Session):
        meal = self.get_today(db)
        if not meal:
            # FIXME: id should be today's date
            self.raise_not_found_error(id="<today>")
        return meal

    def get_tomorrow_or_404(self, db: Session):
        meal = self.get_tomorrow(db)
        if not meal:
            # FIXME: id should be tomorrow's date
            self.raise_not_found_error(id="<tomorrow>")
        return meal

    def get_by_date_delta(self, db: Session, *, delta_days: int):
        tomorrow = (datetime.now() + timedelta(days=delta_days)).date()
        return self.get(db, id=tomorrow)

    def get_today(self, db: Session):
        return self.get_by_date_delta(db, delta_days=0)

    def get_tomorrow(self, db: Session):
        return self.get_by_date_delta(db, delta_days=1)

    def get_day_after_tomorrow(self, db: Session):
        return self.get_by_date_delta(db, delta_days=2)

    def get_week(self, db: Session, *, week: int):
        return db.query(self.model).filter(func.weekofyear(self.model.id) == week).all()

    def get_week_delta(self, db: Session, *, delta_weeks: int):
        week = get_current_week() + delta_weeks
        return self.get_week(db, week=week)

    def get_current_week(self, db: Session):
        week = get_current_week()
        return self.get_week(db, week=week)

    def remove_week(self, db: Session, *, week: int):
        meals = self.get_week(db, week=week)
        for meal in meals:
            self.remove(db, id=meal.id)

    def remove_current_week(self, db: Session):
        week = get_current_week()
        self.remove_week(db, week=week)


meal = CRUDMeal(Meal)
