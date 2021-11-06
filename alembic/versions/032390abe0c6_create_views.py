"""Create views

Revision ID: 032390abe0c6
Revises: f2b0ccdc9f11
Create Date: 2021-11-06 21:00:05.760482

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "032390abe0c6"
down_revision = "f2b0ccdc9f11"
branch_labels = None
depends_on = None


def upgrade():
    currentWeek = "CREATE OR REPLACE VIEW currentWeek AS SELECT * FROM meal WHERE YEARWEEK(id,1) = yearweek(curdate(),1);"
    nextWeek = "CREATE OR REPLACE VIEW nextWeek AS SELECT * FROM meal WHERE YEARWEEK(id,1) = yearweek(CURDATE()+7,1);"
    op.execute(currentWeek)
    op.execute(nextWeek)


def downgrade():
    currentWeek = "DROP VIEW currentWeek"
    nextWeek = "DROP VIEW nextWeek"
    op.execute(currentWeek)
    op.execute(nextWeek)
