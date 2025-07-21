import time

import boto3

# DynamoDB Local endpoint and region
DYNAMODB_ENDPOINT = "http://dynamodb:8000"
REGION = "us-west-2"

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=DYNAMODB_ENDPOINT,
    region_name=REGION,
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
        {'user_id': '1', 'name': 'Alice', 'email': 'alice@example.com'},
        {'user_id': '2', 'name': 'Bob', 'email': 'bob@example.com'},
    ]
    for user in users:
        table.put_item(Item=user)
    print("Seeded initial user data.")

if __name__ == "__main__":
    create_tables()
    time.sleep(2)  # Wait for table to be ready
    seed_data()
    print("DynamoDB initialization complete.")
