"""Base CRUD operations."""

from datetime import date
from typing import Generic, List, Optional, Type, TypeVar

from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db.base_class import Base

Model = TypeVar("Model", bound=Base)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)

_Id = date
# pylint: disable=redefined-builtin


class CRUDBase(Generic[Model, CreateSchema, UpdateSchema]):
    """Base CRUD class."""

    def raise_not_found_error(self, *, id: _Id):
        """Raise 404 NOT FOUND."""
        detail = f"{self.model.__name__} with id={id} does not exist"
        raise HTTPException(404, detail)

    def raise_conflict_error(self, id: _Id):
        """Raise 409 CONFLICT."""
        detail = f"{self.model.__name__} with id={id} already exists"
        raise HTTPException(409, detail)

    def __init__(self, model: Type[Model]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: _Id) -> Optional[Model]:
        """Get an object using its id."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_or_404(self, db: Session, id: _Id) -> Model:
        """Get an object or return 404."""
        obj = self.get(db, id=id)
        if obj is not None:
            return obj
        return self.raise_not_found_error(id=id)

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Model]:
        """Get multiple objects."""

        return db.query(self.model).offset(skip).limit(limit).all()

    def create(
        self, db: Session, *, obj_in: CreateSchema, commit_refresh=True
    ) -> Model:
        """Create an object."""

        obj_in_data = obj_in.dict()
        if "id" in obj_in_data and self.get(db, id=obj_in_data["id"]):
            self.raise_conflict_error(id=obj_in_data["id"])

        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        if commit_refresh:
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(
        db: Session,
        *,
        db_obj: Model,
        obj_in: UpdateSchema,
    ) -> Model:
        """Update an object."""

        obj_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: _Id) -> None:
        """Remove an object."""
        obj = self.get_or_404(db, id=id)
        db.delete(obj)
        db.commit()
