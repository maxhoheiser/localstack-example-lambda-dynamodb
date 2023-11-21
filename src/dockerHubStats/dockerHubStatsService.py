import logging
from typing import Tuple

import requests

logger = logging.getLogger(__name__)


class DockerHubService:
    """
    Handles read and write DockerHub API operations
    """

    def __init__(self, user_name: str, image_name: str) -> None:
        self.user_name = user_name
        self.image_name = image_name

    def get_dockerhub_image_stats(self) -> Tuple[int, int]:
        api_url = f"https://hub.docker.com/v2/repositories/{self.user_name}/{self.image_name}/"

        try:
            response = requests.get(api_url)
        except Exception as e:
            logger.error(f"Error: Unable to fetch data. Exception: {e}")
            raise

        if response.status_code == 200:
            image_data = response.json()
            pull_count = image_data["pull_count"]
            star_count = image_data["star_count"]
            return pull_count, star_count
        else:
            logger.error(
                f"Error: Unable to fetch data. Status Code: {response.status_code}"
            )
            raise


if __name__ == "__main__":
    user_name = "localstack"
    image_name = "localstack"

    LocalStackDockerHubService = DockerHubService(user_name, image_name)
    pull_count, star_count = LocalStackDockerHubService.get_dockerhub_image_stats()

    if pull_count is not None and star_count is not None:
        print(f"Pull Count: {pull_count}")
        print(f"Star Count: {star_count}")
