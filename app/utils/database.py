# DynamoDB connection setup
import os

import aioboto3

DYNAMODB_ENDPOINT_URL = os.getenv("DYNAMODB_ENDPOINT_URL", None)
DYNAMODB_REGION = os.getenv("DYNAMODB_REGION", "us-east-1")


async def get_db():
    """
    Yields an aioboto3 DynamoDB resource for async database operations.
    """
    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        region_name=DYNAMODB_REGION,
        endpoint_url=DYNAMODB_ENDPOINT_URL
    ) as dynamodb_resource:
        yield dynamodb_resource
