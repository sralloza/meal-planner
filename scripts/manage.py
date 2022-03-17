"""Script to create a full week's menu."""

import datetime
import json
import locale
import re
from pathlib import Path
from typing import List
from urllib.parse import urljoin

import click
import requests
from dateutil.parser import parse
from fastapi.encoders import jsonable_encoder
from pydantic import parse_file_as, parse_obj_as
from ruamel.yaml import YAML

from app.core.config import settings
from app.schemas.meal import Meal

PATTERN = r"## (?P<weekday>[\wáéó]+)\n(?P<lunch>[\[\]\-\/()\wáéó\n ]+)\n(?P<dinner>[\[\]\-\/()\wáéó\n ]+)\n"
MD_DIR = Path(__file__).parent.parent / "docs"
MD_FILES = [x.stem for x in MD_DIR.iterdir() if x.suffix == ".md" and x.stem.isdigit()]
YML_FILES = [x.stem for x in MD_DIR.iterdir() if x.suffix == ".yml"]
JSON_FILES = [x.stem for x in MD_DIR.iterdir() if x.suffix == ".json"]

try:
    locale.setlocale(locale.LC_ALL, "es_ES.utf8")
except locale.Error:
    locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")

yaml = YAML()


class ModifiedMeal(Meal):
    date: datetime.date


@click.group()
def cli():
    pass


@cli.command("md-yml")
@click.argument("date", metavar="DATE", type=click.Choice(MD_FILES))
def convert_md_to_yml(date: str):
    filepath = MD_DIR / f"{date}.md"
    data = filepath.read_text("utf8").splitlines()
    joined = "\n".join([x for x in data if x]) + "\n"

    matches = re.finditer(PATTERN, joined)

    current_year = datetime.datetime.now().year
    week_number = int(date)

    objs = []
    for match in matches:
        parsed = match.groupdict()
        weekday = parsed["weekday"]
        meal_date = datetime.datetime.strptime(
            f"{weekday} {week_number} {current_year}", "%A %W %Y"
        ).date()

        lunch = [x.strip("- ") for x in parsed["lunch"].splitlines()]
        if len(lunch) == 2:
            lunch1, lunch2 = lunch
        else:
            lunch1, lunch2 = lunch[0], None

        dinner = parsed["dinner"].strip("- ")
        obj = dict(date=meal_date, lunch1=lunch1, lunch2=lunch2, dinner=dinner)
        if "[C]" in lunch1:
            obj["lunch1_frozen"] = True
            obj["lunch1"] = obj["lunch1"].replace("[C] ", "")
        if lunch2 and "[C]" in lunch2:
            obj["lunch2_frozen"] = True
            obj["lunch2"] = obj["lunch2"].replace("[C] ", "")
        if "[C]" in dinner:
            obj["dinner_frozen"] = True
            obj["dinner"] = obj["dinner"].replace("[C] ", "")
        objs.append(obj)

    yaml_path = MD_DIR / f"{date}.yml"
    if yaml_path.is_file():
        with yaml_path.open("rt", encoding="utf8") as fh:
            current_data = yaml.load(fh)

        if current_data == objs:
            click.secho("Not modified", fg="bright_yellow")
            return

        click.confirm(
            "YML file exists and will be modified. Continue?", abort=True, default=True
        )

    with yaml_path.open("wt", encoding="utf8") as fh:
        current_data = yaml.dump(objs, fh)
    unparsed_data = yaml_path.read_text("utf8")
    yaml_path.write_text(re.sub("(- date:)", r"\n\1", unparsed_data), encoding="utf8")


@cli.command("confirm")
@click.argument("date", metavar="DATE", type=click.Choice(YML_FILES))
@click.option("--dry-run", "-n", is_flag=True, help="Dry run mode")
@click.argument("API_URL", envvar="MEAL_PLANNER_API_URL", required=False)
def upload_yml(date: str, api_url: str, dry_run: bool):
    convert_yml_json(date)
    if not dry_run:
        upload_json(date, api_url)


@cli.command("yml-json")
@click.argument("date", metavar="DATE", type=click.Choice(YML_FILES))
def convert_yml_json_cli(date: str):
    convert_yml_json(date)


def convert_yml_json(date: str):
    filepath = MD_DIR / f"{date}.yml"
    with filepath.open("rt", encoding="utf8") as fh:
        objs = yaml.load(fh)

    parsed_data = parse_obj_as(List[ModifiedMeal], objs)

    json_path = MD_DIR / f"{date}.json"
    if json_path.is_file():
        current_data = parse_file_as(List[ModifiedMeal], json_path, encoding="utf8")

        if current_data == parsed_data:
            click.secho("Not modified", fg="bright_yellow")
            return

        click.confirm(
            "JSON file exists and will be modified. Continue?", abort=True, default=True
        )

    with json_path.open("wt", encoding="utf8") as fh:
        json.dump(jsonable_encoder(parsed_data), fh, indent=2, ensure_ascii=False)


def upload_json(date: str, api_url: str):
    filepath = MD_DIR / f"{date}.json"
    headers = {"x-token": settings.API_TOKEN, "user-agent": "mealer"}

    url = urljoin(api_url, "/meals/bulk")
    data = json.loads(filepath.read_text("utf8"))
    r = requests.post(url, json=data, headers=headers)
    print(r.json())
    r.raise_for_status()


if __name__ == "__main__":
    cli(prog_name="meal-manager")
