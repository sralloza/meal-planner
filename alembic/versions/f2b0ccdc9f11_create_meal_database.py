"""Create Meal database

Revision ID: f2b0ccdc9f11
Revises:
Create Date: 2021-10-10 21:35:15.673461

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "f2b0ccdc9f11"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "meal",
        sa.Column("id", sa.Date(), nullable=False),
        sa.Column("L1", sa.String(length=100), nullable=False),
        sa.Column("L1.frozen", sa.Boolean(), nullable=False),
        sa.Column("L2", sa.String(length=100), nullable=True),
        sa.Column("L2.frozen", sa.Boolean(), nullable=False),
        sa.Column("D", sa.String(length=100), nullable=False),
        sa.Column("D.frozen", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meal_D"), "meal", ["D"], unique=False)
    op.create_index(op.f("ix_meal_D.frozen"), "meal", ["D.frozen"], unique=False)
    op.create_index(op.f("ix_meal_L1"), "meal", ["L1"], unique=False)
    op.create_index(op.f("ix_meal_L1.frozen"), "meal", ["L1.frozen"], unique=False)
    op.create_index(op.f("ix_meal_L2"), "meal", ["L2"], unique=False)
    op.create_index(op.f("ix_meal_L2.frozen"), "meal", ["L2.frozen"], unique=False)
    op.create_index(op.f("ix_meal_id"), "meal", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_meal_id"), table_name="meal")
    op.drop_index(op.f("ix_meal_L2.frozen"), table_name="meal")
    op.drop_index(op.f("ix_meal_L2"), table_name="meal")
    op.drop_index(op.f("ix_meal_L1.frozen"), table_name="meal")
    op.drop_index(op.f("ix_meal_L1"), table_name="meal")
    op.drop_index(op.f("ix_meal_D.frozen"), table_name="meal")
    op.drop_index(op.f("ix_meal_D"), table_name="meal")
    op.drop_table("meal")
    # ### end Alembic commands ###
