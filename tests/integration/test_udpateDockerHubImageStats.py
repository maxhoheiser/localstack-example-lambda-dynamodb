import json
from datetime import datetime

import boto3
import pytest

IMAGE_PULL = 100
IMAGE_STAR = 50

input_string = "2022-01-01T00:00:00Z"
datetime_object = datetime.strptime(input_string, "%Y-%m-%dT%H:%M:%SZ")
DATE_TIME = datetime_object.isoformat()


awslambda = boto3.client(
    "lambda", endpoint_url="http://localhost.localstack.cloud:4566"
)


@pytest.fixture(autouse=True)
def _wait_for_lambdas():
    awslambda.get_waiter("function_active").wait(
        FunctionName="update_docker_hub_image_stats"
    )


def test_lambda_handler():
    response = awslambda.invoke(
        FunctionName="update_docker_hub_image_stats",
        InvocationType="RequestResponse",
        Payload=json.dumps({"None": "None"}),
    )

    payload = json.loads(response["Payload"].read())
    # need to use payload status code, since response status code is always 200
    statusCode = payload.get("statusCode")
    # body = payload.get("body")

    assert statusCode == 200
    # extend this test with mock DockerHubService and get_iso_date_time_now return values
    # assert (
    #    body
    #    == f"successful update for dynamoDB table: localstack, for pull_count: {IMAGE_PULL}
    # and star_count: {IMAGE_STAR}, at date_time: {DATE_TIME}"
    # )


if __name__ == "__main__":
    pytest.main()
