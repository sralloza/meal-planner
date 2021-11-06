"""Load docs script."""

import locale
from itertools import groupby
from pathlib import Path
from typing import List

import click
from pydantic.tools import parse_obj_as
from ruamel.yaml import YAML

from app import crud
from app.core.aws import get_meals
from app.deps.database import manual_db
from app.schemas.meal import Meal

MD_DIR = Path(__file__).parent.with_name("docs")
MKDOCS_YML_PATH = Path(__file__).parent.parent / "mkdocs.yml"
locale.setlocale(locale.LC_ALL, "es_ES.utf8")
yml = YAML()
yml.indent(offset=2, sequence=4)


@click.command()
@click.argument("source", type=click.Choice(["aws", "db"]))
def load_docs(source: str):
    """Load the docs from AWS or the database."""
    if source == "aws":
        meals = get_meals()
    else:
        with manual_db() as db:
            meals = parse_obj_as(List[Meal], crud.meal.get_multi(db))

    weeks = []
    for week, weekly_meals in groupby(meals, lambda x: x.id.isocalendar()[1]):
        weeks.append(week)
        weekly_meals = list(weekly_meals)
        create_md(week, weekly_meals)

    rebuild_mkdocs_yml(weeks)


def create_md(week: int, weekly_meals: List[Meal]):
    """Creates the markdown file."""
    MD_DIR.mkdir(exist_ok=True)
    md_filepath = MD_DIR / f"{week}.md"
    content = ""
    weekly_meals.sort(key=lambda x: x.id)

    for i, meal in enumerate(weekly_meals):
        if not i:
            content += f"# Semana {meal.id}\n"

        content += f"\n## {meal.id.strftime('%A').title()}\n\n"
        content += f"- {meal.lunch1}\n"
        if meal.lunch2:
            content += f"- {meal.lunch2}\n"
        content += f"\n- {meal.dinner}\n"

    md_filepath.write_text(content, "utf8")


def rebuild_mkdocs_yml(weeks: List[int]):
    """Rebuilds the mkdocs.yml file."""
    with MKDOCS_YML_PATH.open("rt", encoding="utf8") as fh:
        yml_content = yml.load(fh)
    yml_content["nav"] = [{"Índice": "index.md"}]
    yml_content["nav"] += [{f"Semana {x}": f"{x}.md"} for x in weeks]

    with MKDOCS_YML_PATH.open("wt", encoding="utf8") as fh:
        yml.dump(yml_content, fh)


if __name__ == "__main__":
    load_docs()
