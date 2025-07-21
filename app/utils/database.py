# DynamoDB connection setup
import os

import boto3

DYNAMODB_ENDPOINT_URL = os.getenv("DYNAMODB_ENDPOINT_URL", None)
DYNAMODB_REGION = os.getenv("DYNAMODB_REGION", "us-east-1")

dynamodb_resource = boto3.resource(
    "dynamodb",
    region_name=DYNAMODB_REGION,
    endpoint_url=DYNAMODB_ENDPOINT_URL
)

def get_db():
    """
    Yields a DynamoDB resource for database operations.
    """
    yield dynamodb_resource
