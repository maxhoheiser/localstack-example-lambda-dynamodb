import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.dynamoDB.dynamoDBService import DynamoDBService

TABLE_NAME = "my_table"
ENDPOINT_URL = "http://localhost:8000"

USER_NAME = "john"
IMAGE_NAME = "my_image"
PULL_COUNT = 100
STAR_COUNT = 50

input_string = "2022-01-01T00:00:00Z"
datetime_object = datetime.strptime(input_string, "%Y-%m-%dT%H:%M:%SZ")
DATE_TIME = datetime_object.isoformat()


class TestDynamoDBService(unittest.TestCase):
    def setUp(self):
        self.table_name = TABLE_NAME
        self.endpoint_url = ENDPOINT_URL

        self.patcher = patch("src.dynamoDB.dynamoDBService.boto3.resource")
        self.mocked_boto3_resource = self.patcher.start()
        self.mocked_dyn_resource = MagicMock()
        self.mocked_boto3_resource.return_value = self.mocked_dyn_resource
        self.service = DynamoDBService(self.table_name, self.endpoint_url)

    def tearDown(self):
        self.patcher.stop()

    def test_get_table_existing_table(self):
        table_name = TABLE_NAME
        self.service.table_exists = MagicMock(return_value=True)
        self.service.dyn_resource.Table = MagicMock(return_value=MagicMock())

        table = self.service.get_table(table_name)

        self.service.table_exists.assert_called_once_with(table_name)
        self.service.dyn_resource.Table.assert_called_once_with(table_name)
        self.assertEqual(table, self.service.dyn_resource.Table.return_value)

    def test_get_table_non_existing_table(self):
        table_name = TABLE_NAME
        self.service.table_exists = MagicMock(return_value=False)
        self.service.create_table = MagicMock(return_value=MagicMock())

        table = self.service.get_table(table_name)

        self.service.table_exists.assert_called_once_with(table_name)
        self.service.create_table.assert_called_once_with(table_name)
        self.assertEqual(table, self.service.create_table.return_value)

    def test_table_exists_existing_table(self):
        table_name = TABLE_NAME
        self.service.dyn_resource.Table = MagicMock(return_value=MagicMock())
        self.service.dyn_resource.Table.return_value.load = MagicMock()

        exists = self.service.table_exists(table_name)

        self.service.dyn_resource.Table.assert_called_once_with(table_name)
        self.service.dyn_resource.Table.return_value.load.assert_called_once()
        self.assertTrue(exists)

    def test_create_table_success(self):
        table_name = TABLE_NAME
        self.service.dyn_resource.create_table = MagicMock(return_value=MagicMock())
        self.service.dyn_resource.create_table.return_value.wait_until_exists = (
            MagicMock()
        )

        table = self.service.create_table(table_name)

        self.service.dyn_resource.create_table.assert_called_once_with(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "date_time", "KeyType": "HASH"},
                {"AttributeName": "image_name", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "date_time", "AttributeType": "S"},
                {"AttributeName": "image_name", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        self.service.dyn_resource.create_table.return_value.wait_until_exists.assert_called_once()
        self.assertEqual(table, self.service.dyn_resource.create_table.return_value)

    def test_create_table_error(self):
        table_name = TABLE_NAME
        self.service.dyn_resource.create_table = MagicMock(side_effect=Exception())

        with self.assertRaises(Exception):
            self.service.create_table(table_name)

    def test_write_dockerhub_stats_success(self):
        user_name = USER_NAME
        image_name = IMAGE_NAME
        pull_count = PULL_COUNT
        star_count = STAR_COUNT
        date_time = DATE_TIME
        self.service.table.put_item = MagicMock()

        self.service.write_dockerhub_stats(
            user_name, image_name, pull_count, star_count, date_time
        )

        self.service.table.put_item.assert_called_once_with(
            Item={
                "user_name": user_name,
                "image_name": image_name,
                "pull_count": pull_count,
                "star_count": star_count,
                "date_time": date_time,
            }
        )

    def test_write_dockerhub_stats_error(self):
        user_name = USER_NAME
        image_name = IMAGE_NAME
        pull_count = PULL_COUNT
        star_count = STAR_COUNT
        date_time = DATE_TIME
        self.service.table.put_item = MagicMock(side_effect=Exception())

        with self.assertRaises(Exception):
            self.service.write_dockerhub_stats(
                user_name, image_name, pull_count, star_count, date_time
            )

    def test_read_dockerhub_stats_success(self):
        user_name = USER_NAME
        image_name = IMAGE_NAME
        pull_count = PULL_COUNT
        star_count = STAR_COUNT
        date_time = DATE_TIME
        response_item = {
            "user_name": user_name,
            "image_name": image_name,
            "pull_count": pull_count,
            "star_count": star_count,
            "date_time": date_time,
        }
        self.service.table.get_item = MagicMock(return_value={"Item": response_item})

        response = self.service.read_dockerhub_stats(date_time, image_name)

        self.service.table.get_item.assert_called_once_with(
            Key={"date_time": date_time, "image_name": image_name}
        )
        self.assertEqual(response, response_item)

    def test_read_dockerhub_stats_error(self):
        user_name = USER_NAME
        image_name = IMAGE_NAME
        self.service.table.get_item = MagicMock(side_effect=Exception())

        with self.assertRaises(Exception):
            self.service.read_dockerhub_stats(user_name, image_name)

    def test_clean_up_success(self):
        self.service.table.delete = MagicMock()

        self.service.clean_up()

        self.service.table.delete.assert_called_once()

    def test_clean_up_error(self):
        self.service.table.delete = MagicMock(side_effect=Exception())

        with self.assertRaises(Exception):
            self.service.clean_up()


if __name__ == "__main__":
    unittest.main()
