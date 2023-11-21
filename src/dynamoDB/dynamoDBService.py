import logging
import time
from typing import Any

import boto3
from botocore.exceptions import ClientError

from src.utils.helper import get_iso_date_time_now
from src.utils.types import IsoDateTimeString

logger = logging.getLogger(__name__)


class DynamoDBService:
    """
    Handles read and write DynamoDB operations
    """

    def __init__(self, table_name: str, endpoint_url: str) -> None:
        self.dyn_resource = boto3.resource("dynamodb", endpoint_url=endpoint_url)
        self.table = self.get_table(table_name)

    def get_table(self, table_name: str) -> Any:
        """
        Returns a DynamoDB table
        """
        if self.table_exists(table_name):
            table = self.dyn_resource.Table(table_name)
        else:
            table = self.create_table(table_name)
        return table

    def table_exists(self, table_name) -> bool:
        """
        Determines whether a table exists
        """
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                exists = False
            else:
                logger.error(
                    "Couldn't check for existence of %s. Here's why: %s: %s",
                    table_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
        return exists

    def create_table(self, table_name: str) -> Any:
        """
        Creates a DynamoDB table
        """
        try:
            table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "date_time", "KeyType": "HASH"},
                    {"AttributeName": "image_name", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "date_time", "AttributeType": "S"},
                    {"AttributeName": "image_name", "AttributeType": "S"},
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            )
            table.wait_until_exists()
        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s",
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return table

    def write_dockerhub_stats(
        self,
        user_name: str,
        image_name: str,
        pull_count: int,
        star_count: int,
        date_time: IsoDateTimeString,
    ) -> None:
        """
        Adds dockerhub stats to the DynamoDB table
        """
        try:
            self.table.put_item(
                Item={
                    "user_name": user_name,
                    "image_name": image_name,
                    "pull_count": pull_count,
                    "star_count": star_count,
                    "date_time": date_time,
                }
            )

        except ClientError as err:
            logger.error(
                "Couldn't add dockerhubStats %s to table %s. Here's why: %s: %s",
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def read_dockerhub_stats(self, date_time: str, image_name: str) -> Any:
        """
        Reads dockerhub stats from the DynamoDB table
        """
        try:
            response = self.table.get_item(
                Key={"date_time": date_time, "image_name": image_name}
            )
            return response["Item"]

        except ClientError as err:
            logger.error(
                "Couldn't read dockerhubStats %s from table %s. Here's why: %s: %s",
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def clean_up(self) -> None:
        """
        Deletes the DynamoDB table
        """
        try:
            self.table.delete()
        except ClientError as err:
            logger.error(
                "Couldn't delete table %s. Here's why: %s: %s",
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise


if __name__ == "__main__":
    table_name = "dockerhubStats"
    user_name = "localstack"
    image_name = "localstack"
    pull_count = 100
    star_count = 100

    endpoint_url = "http://localhost:8000"
    dynamoDBService = DynamoDBService(table_name, endpoint_url)

    for _ in range(10):
        date_time = get_iso_date_time_now()
        dynamoDBService.write_dockerhub_stats(
            user_name, image_name, pull_count, star_count, date_time
        )
        time.sleep(1)

    response = dynamoDBService.table.scan()

    items = response.get("Items", [])
    for item in items:
        print(item)

    dynamoDBService.clean_up()
