import logging

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI

DYNAMODB_ENDPOINT = "http://dynamodb:8000"
REGION = "us-west-2"

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=DYNAMODB_ENDPOINT,
    region_name=REGION,
    aws_access_key_id='dummy',
    aws_secret_access_key='dummy'
)

def create_users_table():
    try:
        table = dynamodb.create_table(
            TableName='users',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'N'},
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName='users')
        logging.info("Table 'users' created.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            logging.info("Table 'users' already exists.")
        else:
            raise

def create_events_table():
    try:
        table = dynamodb.create_table(
            TableName='events',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'N'},
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName='events')
        logging.info("Table 'events' created.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            logging.info("Table 'events' already exists.")
        else:
            raise

def create_event_registrations_table():
    try:
        table = dynamodb.create_table(
            TableName='event_registrations',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'N'},
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName='event_registrations')
        logging.info("Table 'event_registrations' created.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            logging.info("Table 'event_registrations' already exists.")
        else:
            raise

def create_event_hosts_table():
    try:
        table = dynamodb.create_table(
            TableName='event_hosts',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'N'},
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName='event_hosts')
        logging.info("Table 'event_hosts' created.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            logging.info("Table 'event_hosts' already exists.")
        else:
            raise

def init_dynamodb():
    create_users_table()
    create_events_table()
    create_event_registrations_table()
    create_event_hosts_table()
    logging.info("DynamoDB tables initialized.")
    seed_all_tables()

# --- Seed Data ---
def seed_all_tables():
    # Users
    users_table = dynamodb.Table('users')
    users = [
        {'id': 1, 'first_name': 'Alice', 'last_name': 'Smith', 'email': 'alice@example.com', 'role': 'attendee'},
        {'id': 2, 'first_name': 'Bob', 'last_name': 'Johnson', 'email': 'bob@example.com', 'role': 'host'},
    ]
    for user in users:
        users_table.put_item(Item=user)
    logging.info("Seeded users table.")

    # Events
    events_table = dynamodb.Table('events')
    events = [
        {'id': 1, 'slug': 'event-1', 'title': 'First Event', 'owner_id': 2, 'start_at': '2025-07-21T10:00:00', 'end_at': '2025-07-21T12:00:00'},
        {'id': 2, 'slug': 'event-2', 'title': 'Second Event', 'owner_id': 2, 'start_at': '2025-07-22T14:00:00', 'end_at': '2025-07-22T16:00:00'},
    ]
    for event in events:
        events_table.put_item(Item=event)
    logging.info("Seeded events table.")

    # Event Registrations
    registrations_table = dynamodb.Table('event_registrations')
    registrations = [
        {'id': 1, 'user_id': 1, 'event_id': 1},
        {'id': 2, 'user_id': 1, 'event_id': 2},
    ]
    for reg in registrations:
        registrations_table.put_item(Item=reg)
    logging.info("Seeded event_registrations table.")

    # Event Hosts
    hosts_table = dynamodb.Table('event_hosts')
    hosts = [
        {'id': 1, 'event_id': 1, 'user_id': 2},
        {'id': 2, 'event_id': 2, 'user_id': 2},
    ]
    for host in hosts:
        hosts_table.put_item(Item=host)
    logging.info("Seeded event_hosts table.")

# FastAPI event hook

def register_dynamodb_init(app: FastAPI):
    @app.on_event("startup")
    async def startup_event():
        init_dynamodb()
