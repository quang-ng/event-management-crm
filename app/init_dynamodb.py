import os
import time

import boto3


DYNAMODB_ENDPOINT_URL = os.getenv("DYNAMODB_ENDPOINT_URL", None)
DYNAMODB_REGION = os.getenv("DYNAMODB_REGION", "us-east-1")

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=DYNAMODB_ENDPOINT_URL,
    region_name=DYNAMODB_REGION,
    aws_access_key_id='dummy',
    aws_secret_access_key='dummy'
)

def create_tables():
    # Example: Create a table named 'users'
    try:
        table = dynamodb.create_table(
            TableName='users',
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Creating table 'users'...")
        table.meta.client.get_waiter('table_exists').wait(TableName='users')
        print("Table 'users' created.")
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("Table 'users' already exists.")

def seed_data():
    table = dynamodb.Table('users')
    # Example seed data
    users = [
        
    ]
    for user in users:
        table.put_item(Item=user)
    print("Seeded initial user data.")

if __name__ == "__main__":
    create_tables()
    time.sleep(2)  # Wait for table to be ready
    seed_data()
    print("DynamoDB initialization complete.")
