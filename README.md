# LocalStack example using AWS Lambda and DynamoDB

| Key          | Value                                                        |
| ------------ | ------------------------------------------------------------ |
| Services     | Lambda, DynamoDB, Event Bridge                               |
| Integrations | AWS SDK, AWS CLI, GitHub actions, pytest                     |
| Categories   | Serverless, DynamoDB, LocalStack developer endpoints, Python |
| Level        | Intermediate                                                 |

## Description

This app queries [DockerHub](https://hub.docker.com/) to get the number of pulls and stars for a given image. This information is stored in a DynamoDB table, indexed by the query time. The app is deployed as an AWS Lambda function and uses the AWS SDK to interact with DynamoDB. A Event Bridge is used to trigger the Lambda function each minute. The app is tested using pytest and awslocal using the localstack docker container.

## Getting Started

### Dependencies

LocalStack cli and docker container

### Installing

create a virtual environment and install the requirements

```bash
pip install -r requirements-dev.txt
pre-commit install
commit-linter
```

### Run the program

1. Start localstack

   ```bash
   localstack start
   ```

2. Deploy the lambda function and provision the DynamoDB table

   ```bash
   sh bin/deploy.sh
   ```

### Testing

- run unit tests

  ```bash
  make test
  ```

- run integration tests:

  ```bash
  make integration-test
  ```

- GitHub actions CI tests
  `.github/workflows/test-integration-localstack.yaml`
