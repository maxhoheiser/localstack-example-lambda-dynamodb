import os
from typing import Any, Dict

from src.dockerHubStats.dockerHubStatsService import DockerHubService
from src.dynamoDB.dynamoDBService import DynamoDBService
from src.utils.helper import get_iso_date_time_now


def lambda_handler(event, context) -> Dict[str, Any]:
    user_name = "localstack"
    image_name = "localstack"

    endpoint_url = get_endpoint_url()
    table_name = "localstack"

    try:
        LocalStackDockerHubService = DockerHubService(user_name, image_name)
        date_time = get_iso_date_time_now()
        pull_count, star_count = LocalStackDockerHubService.get_dockerhub_image_stats()

        LocalStackDynamoDBService = DynamoDBService(table_name, endpoint_url)
        LocalStackDynamoDBService.write_dockerhub_stats(
            user_name, image_name, pull_count, star_count, date_time
        )

        return {
            "statusCode": 200,
            "body": (
                f"successful update for dynamoDB table: {table_name}, "
                f"for pull_count: {pull_count} and star_count: {star_count}, "
                f"at date_time: {date_time}"
            ),
        }

    except Exception as err:
        return {
            "statusCode": 500,
            "body": f"Internal Server Error: {err}",
        }


def get_endpoint_url():
    try:
        LOCALSTACK_HOSTNAME = os.environ["LOCALSTACK_HOSTNAME"]
        endpoint_url = f"http://{LOCALSTACK_HOSTNAME}:4566"
    except KeyError:
        endpoint_url = os.environ.get("DYNAMODB_ENDPOINT_URL")

    return endpoint_url


if __name__ == "__main__":
    print(lambda_handler(None, None))
