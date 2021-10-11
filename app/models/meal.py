from sqlalchemy import Boolean, Column, Date, String
from sqlalchemy.orm import synonym

from ..db.base_class import Base

# pylint: disable=too-few-public-methods


class Meal(Base):
    id = Column(Date(), primary_key=True, index=True)
    date = synonym("id")

    lunch1 = Column("L1", String(100), index=True, nullable=False)
    lunch1_frozen = Column("L1.frozen", Boolean(), index=True, nullable=False)

    lunch2 = Column("L2", String(100), index=True, nullable=True)
    lunch2_frozen = Column("L2.frozen", Boolean(), index=True, nullable=False)

    dinner = Column("D", String(100), index=True, nullable=False)
    dinner_frozen = Column("D.frozen", Boolean(), index=True, nullable=False)
