import tempfile
from json import dumps
from typing import List

import boto3
from botocore.exceptions import ClientError
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from pydantic import parse_raw_as

from ..core.config import settings
from ..schemas.meal import Meal


def get_meals() -> List[Meal]:
    s3 = boto3.client("s3")
    with tempfile.TemporaryFile() as fp:
        try:
            s3.download_fileobj(settings.S3_BUCKET_NAME, settings.S3_FILE_NAME, fp)
        except ClientError as exc:
            if "404" in str(exc):
                raise HTTPException(404, "Meal not found")
            raise

        fp.seek(0)
        return parse_raw_as(List[Meal], fp.read().decode("utf8"))


def save_meals(meals: List[Meal]):
    menu_json = dumps(jsonable_encoder(meals))
    s3 = boto3.client("s3")
    with tempfile.TemporaryFile() as fp:
        fp.write(menu_json.encode("utf8"))
        fp.seek(0)
        try:
            s3.upload_fileobj(fp, settings.S3_BUCKET_NAME, settings.S3_FILE_NAME)
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchBucket":
                create_bucket()
                return save_meals(meals)
            raise


def create_bucket():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)
