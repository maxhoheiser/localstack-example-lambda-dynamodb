os=$(uname -s)
if [ "$os" == "Linux" ]; then
    (
        cd lambdas/updateDockerHubImageStats
        rm -rf package lambda.zip
        mkdir package
        pip install -r requirements.txt -t package
        cp -r ../../src libs/src
        zip lambda.zip lambda_function.py
        cd package
        zip -r ../lambda.zip *;
    )
else
    (
    cd lambdas/updateDockerHubImageStats
    rm -rf libs lambda.zip
    docker run --platform linux/x86_64 -v "$PWD":/var/task "public.ecr.aws/sam/build-python3.10" /bin/sh -c "pip install -r requirements.txt -t libs; exit"
    cp -r ../../src libs/src
    cd libs && zip -r ../lambda.zip . && cd ..
    zip lambda.zip lambda_function.py
    rm -rf libs
    )
fi

awslocal dynamodb create-table \
    --table-name localstack \
    --key-schema AttributeName=user_name,KeyType=HASH AttributeName=image_name,KeyType=RANGE \
    --attribute-definitions AttributeName=user_name,AttributeType=S AttributeName=image_name,AttributeType=S \
    --billing-mode PAY_PER_REQUEST \
    --region ap-south-1

awslocal lambda create-function \
    --function-name update_docker_hub_image_stats \
    --runtime python3.10 \
    --timeout 10 \
    --zip-file fileb://lambdas/updateDockerHubImageStats/lambda.zip \
    --handler lambda_function.lambda_handler \
    --dead-letter-config TargetArn=arn:aws:sns:eu-west-1:000000000000:failed-resize-topic \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --environment Variables="{STAGE=local}"

rm -rf lambdas/updateDockerHubImageStats/lambda.zip

awslocal lambda wait function-active-v2 --function-name update_docker_hub_image_stats
awslocal lambda create-function-url-config \
    --function-name update_docker_hub_image_stats \
    --auth-type NONE

lambda_url=$(awslocal lambda list-function-url-configs --function-name update_docker_hub_image_stats | jq -r '.FunctionUrlConfigs[0].FunctionUrl')
curl -v $lambda_url
