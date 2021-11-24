"""Load docs script."""

from datetime import datetime
import locale
from itertools import groupby
from pathlib import Path
from typing import List

import click
from pydantic.tools import parse_obj_as
from ruamel.yaml import YAML

from app import crud
from app.core.aws import get_meals
from app.core.config import settings
from app.deps.database import manual_db
from app.schemas.meal import Meal

MD_DIR = Path(__file__).parent.with_name("docs")
MKDOCS_YML_PATH = Path(__file__).parent.parent / "mkdocs.yml"
locale.setlocale(locale.LC_ALL, "es_ES.utf8")
yml = YAML()
yml.indent(offset=2, sequence=4)


@click.command()
@click.argument("source", type=click.Choice(["aws", "db"]))
@click.option("--extra-week", is_flag=True)
def load_docs(source: str, extra_week: bool):
    """Load the docs from AWS or the database."""
    if source == "aws":
        meals = get_meals()
    else:
        with manual_db() as db:
            meals = parse_obj_as(List[Meal], crud.meal.get_multi(db))

    weeks = []
    week = 0
    for week, weekly_meals in groupby(meals, lambda x: x.id.isocalendar()[1]):
        weeks.append(week)
        weekly_meals = list(weekly_meals)
        create_md(week, weekly_meals)

    if extra_week and week:
        weeks.append(week + 1)
        create_md(week + 1, [], override=False)

    recreate_md_index(weeks)
    rebuild_mkdocs_yml(weeks)


def get_weekdays():
    return [datetime(2001, 1, i).strftime("%A") for i in range(1, 8)]


def get_default_md_text():
    output = "# Semana XXXX-XX-XX\n"

    weekdays = settings.LOCALE_WEEKDAY_NAMES or get_weekdays()

    for weekday in weekdays:
        output += f"\n## {weekday.title()}\n"

    return output


def create_md(week: int, weekly_meals: List[Meal], override=True):
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

    if not content:
        content = get_default_md_text()

    if md_filepath.exists() and not override:
        data = md_filepath.read_text("utf8")
        if content != data:
            click.secho(f"Skipping write of {md_filepath} (override=False)", fg="bright_yellow")
            return


    md_filepath.write_text(content, "utf8")


def recreate_md_index(weeks: List[int]):
    index_path = MKDOCS_YML_PATH.parent / "docs/index.md"
    output = "# Meal Planner - Planificador de comidas\n\n"
    for week in weeks:
        output += f"- [Semana {week}]({week}.md)\n"

    index_path.write_text(output, "utf8")


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
