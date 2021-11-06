"""Script to import data from AWS into the database using the API."""

from urllib.parse import urljoin

import click
import requests
from fastapi.encoders import jsonable_encoder

from app.core.aws import get_meals
from app.core.config import settings


@click.command("import")
@click.argument("API_URL", envvar="MEAL_PLANNER_API_URL")
def import_aws_db(api_url):
    """Imports the data from AWS into the database using the API."""
    click.confirm(f"Import AWS DB to {api_url!r}?", abort=True, default=True)
    headers = {"x-token": settings.API_TOKEN, "user-agent": "mealer"}

    url = urljoin(api_url, "/meals/bulk")
    data = jsonable_encoder(get_meals())
    r = requests.post(url, json=data, headers=headers)

    print(r.json())
    r.raise_for_status()


if __name__ == "__main__":
    import_aws_db()
