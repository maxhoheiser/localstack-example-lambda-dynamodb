import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from src.dockerHubStats.dockerHubStatsService import DockerHubService

USER_NAME: str = "localstack"
IMAGE_NAME: str = "localstack"


class TestDockerHubService(unittest.TestCase):
    def setUp(self) -> None:
        self.user_name: str = USER_NAME
        self.image_name: str = IMAGE_NAME
        self.service: DockerHubService = DockerHubService(
            self.user_name, self.image_name
        )

    @patch("src.dockerHubStats.dockerHubStatsService.requests.get")
    def test_get_dockerhub_image_stats_success(self, mock_get: MagicMock) -> None:
        mock_response: Dict[str, Any] = {"pull_count": 100, "star_count": 50}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        pull_count, star_count = self.service.get_dockerhub_image_stats()

        self.assertEqual(pull_count, 100)
        self.assertEqual(star_count, 50)

    @patch("src.dockerHubStats.dockerHubStatsService.requests.get")
    def test_get_dockerhub_image_stats_error(self, mock_get: MagicMock) -> None:
        mock_get.return_value.status_code = 404

        with self.assertRaises(Exception):
            self.service.get_dockerhub_image_stats()


if __name__ == "__main__":
    unittest.main()
