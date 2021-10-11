import traceback

import click
from sqlalchemy_utils import create_database, database_exists

from app.db.session import engine


def ensure_database() -> None:
    try:
        if not database_exists(engine.url):
            create_database(engine.url)
    except:
        tb = traceback.format_exc()
        click.secho(f"Error executing query:\n\n{tb}", fg="bright_red")
        raise click.Abort()


@click.command()
def main():
    """Creates the database if it doesn't exist (valid for mysql servers)."""
    ensure_database()


if __name__ == "__main__":
    main()
