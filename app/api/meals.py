"""Meal related API endpoints."""

import datetime
from typing import List, Union

from fastapi import APIRouter, BackgroundTasks, Depends
from starlette.responses import Response

from .. import crud
from ..core.meals import SwapMode, paginate, simplify, simplify_asked
from ..cron.update_notion_meals import update_notion_meals
from ..deps.database import get_db
from ..deps.security import token_middleware
from ..schemas.meal import Meal, MealCreate, MealUpdate, SimpleMeal
from ..utils.responses import gen_responses

router = APIRouter(
    tags=["Meals"],
    dependencies=[Depends(token_middleware)],
    **gen_responses({401: "Missing Token", 403: "Invalid token"}),
)


@router.get(
    "",
    response_model_exclude_unset=True,
    response_model=List[Union[Meal, SimpleMeal]],
    summary="Get all meals",
)
def get_meals(
    *, db=Depends(get_db), simple=Depends(simplify_asked), pagination=Depends(paginate)
):
    """Returns all the meals stored in the database."""
    return simplify(crud.meal.get_multi(db, **pagination), List[SimpleMeal], simple)


@router.get(
    "/week/current",
    response_model_exclude_unset=True,
    response_model=List[Union[Meal, SimpleMeal]],
    summary="Get meals of current week",
)
def get_meals_of_current_week(*, db=Depends(get_db), simple=Depends(simplify_asked)):
    """Returns all the meals from current week. Max 7 meals will be returned."""
    return simplify(crud.meal.get_current_week(db), List[SimpleMeal], simple)


@router.get(
    "/week/next",
    response_model_exclude_unset=True,
    response_model=List[Union[Meal, SimpleMeal]],
    summary="Get meals of next week",
)
def get_meals_of_next_week(*, db=Depends(get_db), simple=Depends(simplify_asked)):
    """Returns all the meals from next week. Max 7 meals will be returned."""
    return simplify(
        crud.meal.get_week_delta(db, delta_weeks=1), List[SimpleMeal], simple
    )


@router.get(
    "/week/{week}",
    response_model_exclude_unset=True,
    response_model=List[Union[Meal, SimpleMeal]],
    summary="Get meals of week",
)
def get_meals_of_week(*, week: int, db=Depends(get_db), simple=Depends(simplify_asked)):
    """Returns all the meals from one specific week. Max 7 meals will be returned."""
    return simplify(crud.meal.get_week(db, week=week), List[SimpleMeal], simple)


@router.get(
    "/today",
    response_model_exclude_unset=True,
    response_model=Union[Meal, SimpleMeal],
    summary="Get today meals",
)
def get_today_meals(*, db=Depends(get_db), simple=Depends(simplify_asked)):
    """Returns today's meals."""
    return simplify(crud.meal.get_today_or_404(db), SimpleMeal, simple)


@router.get(
    "/tomorrow",
    response_model_exclude_unset=True,
    response_model=Union[Meal, SimpleMeal],
    summary="Get tomorrow meals",
)
def get_tomorrow_meals(*, db=Depends(get_db), simple=Depends(simplify_asked)):
    """Returns tomorrows's meals."""
    return simplify(crud.meal.get_tomorrow_or_404(db), SimpleMeal, simple)


@router.get(
    "/{date}",
    response_model_exclude_unset=True,
    response_model=Union[Meal, SimpleMeal],
    summary="Get meal by its date",
    **gen_responses({404: "Not Found"}),
)
def get_single_meal(
    *, date: datetime.date, db=Depends(get_db), simple=Depends(simplify_asked)
):
    """Return meal given the date."""
    return simplify(crud.meal.get_or_404(db, id=date), SimpleMeal, simple)


@router.post(
    "",
    response_model=Union[Meal, SimpleMeal],
    status_code=201,
    summary="Create single meal",
    **gen_responses({409: "Date conflict"}),
)
def create_single_meal(
    *,
    meal: MealCreate,
    db=Depends(get_db),
    simple=Depends(simplify_asked),
    background_tasks: BackgroundTasks,
):
    """Create single meal."""
    result = simplify(crud.meal.create(db, obj_in=meal), SimpleMeal, simple)
    background_tasks.add_task(update_notion_meals)
    return result


@router.post(
    "/bulk",
    response_model_exclude_unset=True,
    response_model=List[Union[Meal, SimpleMeal]],
    status_code=201,
    summary="Create multiple meals",
    **gen_responses({409: "Date conflict"}),
)
def create_multiple_meals(
    *,
    meals: List[MealCreate],
    db=Depends(get_db),
    simple=Depends(simplify_asked),
    background_tasks: BackgroundTasks,
):
    """Create multiple meals."""
    result = simplify(
        crud.meal.create_multiple(db, obj_in=meals), List[SimpleMeal], simple
    )
    background_tasks.add_task(update_notion_meals)
    return result


@router.put(
    "/swap",
    response_model=List[Union[Meal, SimpleMeal]],
    response_model_exclude_unset=True,
    summary="Swap meals",
)
def swap_meals(
    *,
    db=Depends(get_db),
    meal_1: datetime.date,
    meal_2: datetime.date,
    mode: SwapMode,
    background_tasks: BackgroundTasks,
):
    """Swaps meal attributes."""
    result = crud.meal.swap(db, date_1=meal_1, date_2=meal_2, mode=mode)
    background_tasks.add_task(update_notion_meals)
    return result


@router.put(
    "/{date}",
    response_model=Union[Meal, SimpleMeal],
    response_model_exclude_unset=True,
    summary="Update meal",
    **gen_responses({404: "Not Found"}),
)
def update_meal(
    *,
    date: datetime.date,
    meal: MealUpdate,
    db=Depends(get_db),
    simple=Depends(simplify_asked),
    background_tasks: BackgroundTasks,
):
    """Update a saved meal."""
    meal_db = crud.meal.get_or_404(db, id=date)
    result = simplify(
        crud.meal.update(db, db_obj=meal_db, obj_in=meal), SimpleMeal, simple
    )
    background_tasks.add_task(update_notion_meals)
    return result


@router.delete(
    "/week/current",
    response_class=Response,
    status_code=204,
    summary="Delete current week meals",
)
def delete_current_week(*, db=Depends(get_db), background_tasks: BackgroundTasks):
    """Delete all meals of a week."""
    crud.meal.remove_current_week(db)
    background_tasks.add_task(update_notion_meals)


@router.delete(
    "/week/{week}",
    response_class=Response,
    status_code=204,
    summary="Delete week meals",
)
def delete_week(*, week: int, db=Depends(get_db), background_tasks: BackgroundTasks):
    """Delete all meals of a week."""
    crud.meal.remove_week(db, week=week)
    background_tasks.add_task(update_notion_meals)


@router.delete(
    "/{date}",
    response_class=Response,
    status_code=204,
    summary="Delete single meal",
    **gen_responses({404: "Not Found"}),
)
def delete_single_meal(
    *, date: datetime.date, db=Depends(get_db), background_tasks: BackgroundTasks
):
    """Delete single meal."""
    crud.meal.remove(db, id=date)
    background_tasks.add_task(update_notion_meals)
