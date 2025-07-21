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
                {'AttributeName': 'company', 'AttributeType': 'S'},
                {'AttributeName': 'job_title', 'AttributeType': 'S'},
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'company-job_title-index',
                    'KeySchema': [
                        {'AttributeName': 'company', 'KeyType': 'HASH'},
                        {'AttributeName': 'job_title', 'KeyType': 'RANGE'},
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                },
                {
                    'IndexName': 'job_title-company-index',
                    'KeySchema': [
                        {'AttributeName': 'job_title', 'KeyType': 'HASH'},
                        {'AttributeName': 'company', 'KeyType': 'RANGE'},
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName='users')
        logging.info("Table 'users' with GSIs created.")
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
        {'id': 1, 'first_name': 'Alice', 'last_name': 'Smith', 'email': 'alice@example.com', 'role': 'attendee', 'company': 'Acme Corp', 'job_title': 'Engineer', 'city': 'New York', 'state': 'NY', 'events_hosted': 2, 'events_attended': 5},
        {'id': 2, 'first_name': 'Bob', 'last_name': 'Johnson', 'email': 'bob@example.com', 'role': 'host', 'company': 'Beta LLC', 'job_title': 'Manager', 'city': 'San Francisco', 'state': 'CA', 'events_hosted': 3, 'events_attended': 2},
        {'id': 3, 'first_name': 'Carol', 'last_name': 'Williams', 'email': 'carol@example.com', 'role': 'attendee', 'company': 'Acme Corp', 'job_title': 'Designer', 'city': 'Boston', 'state': 'MA', 'events_hosted': 0, 'events_attended': 7},
        {'id': 4, 'first_name': 'David', 'last_name': 'Brown', 'email': 'david@example.com', 'role': 'host', 'company': 'Delta Inc', 'job_title': 'Engineer', 'city': 'Austin', 'state': 'TX', 'events_hosted': 1, 'events_attended': 4},
        {'id': 5, 'first_name': 'Eve', 'last_name': 'Davis', 'email': 'eve@example.com', 'role': 'attendee', 'company': 'Beta LLC', 'job_title': 'Manager', 'city': 'Seattle', 'state': 'WA', 'events_hosted': 0, 'events_attended': 3},
        {'id': 6, 'first_name': 'Frank', 'last_name': 'Miller', 'email': 'frank@example.com', 'role': 'attendee', 'company': 'Gamma Co', 'job_title': 'Engineer', 'city': 'Denver', 'state': 'CO', 'events_hosted': 0, 'events_attended': 1},
        {'id': 7, 'first_name': 'Grace', 'last_name': 'Wilson', 'email': 'grace@example.com', 'role': 'host', 'company': 'Acme Corp', 'job_title': 'Manager', 'city': 'Chicago', 'state': 'IL', 'events_hosted': 2, 'events_attended': 6},
        {'id': 8, 'first_name': 'Hank', 'last_name': 'Moore', 'email': 'hank@example.com', 'role': 'attendee', 'company': 'Delta Inc', 'job_title': 'Designer', 'city': 'Miami', 'state': 'FL', 'events_hosted': 0, 'events_attended': 2},
        {'id': 9, 'first_name': 'Ivy', 'last_name': 'Taylor', 'email': 'ivy@example.com', 'role': 'attendee', 'company': 'Gamma Co', 'job_title': 'Engineer', 'city': 'Portland', 'state': 'OR', 'events_hosted': 0, 'events_attended': 4},
        {'id': 10, 'first_name': 'Jack', 'last_name': 'Anderson', 'email': 'jack@example.com', 'role': 'host', 'company': 'Acme Corp', 'job_title': 'Designer', 'city': 'Dallas', 'state': 'TX', 'events_hosted': 1, 'events_attended': 5},
    ]
    for user in users:
        users_table.put_item(Item=user)
    logging.info("Seeded users table.")

    # Events
    events_table = dynamodb.Table('events')
    events = [
        {'id': 1, 'slug': 'event-1', 'title': 'First Event', 'owner_id': 2, 'start_at': '2025-07-21T10:00:00', 'end_at': '2025-07-21T12:00:00'},
        {'id': 2, 'slug': 'event-2', 'title': 'Second Event', 'owner_id': 4, 'start_at': '2025-07-22T14:00:00', 'end_at': '2025-07-22T16:00:00'},
        {'id': 3, 'slug': 'event-3', 'title': 'Design Meetup', 'owner_id': 10, 'start_at': '2025-08-01T09:00:00', 'end_at': '2025-08-01T11:00:00'},
        {'id': 4, 'slug': 'event-4', 'title': 'Tech Talk', 'owner_id': 7, 'start_at': '2025-08-10T15:00:00', 'end_at': '2025-08-10T17:00:00'},
        {'id': 5, 'slug': 'event-5', 'title': 'Manager Roundtable', 'owner_id': 5, 'start_at': '2025-08-15T13:00:00', 'end_at': '2025-08-15T15:00:00'},
    ]
    for event in events:
        events_table.put_item(Item=event)
    logging.info("Seeded events table.")

    # Event Registrations
    registrations_table = dynamodb.Table('event_registrations')
    registrations = [
        {'id': 1, 'user_id': 1, 'event_id': 1},
        {'id': 2, 'user_id': 3, 'event_id': 1},
        {'id': 3, 'user_id': 5, 'event_id': 2},
        {'id': 4, 'user_id': 6, 'event_id': 2},
        {'id': 5, 'user_id': 8, 'event_id': 3},
        {'id': 6, 'user_id': 9, 'event_id': 3},
        {'id': 7, 'user_id': 2, 'event_id': 4},
        {'id': 8, 'user_id': 4, 'event_id': 4},
        {'id': 9, 'user_id': 7, 'event_id': 5},
        {'id': 10, 'user_id': 10, 'event_id': 5},
    ]
    for reg in registrations:
        registrations_table.put_item(Item=reg)
    logging.info("Seeded event_registrations table.")

    # Event Hosts
    hosts_table = dynamodb.Table('event_hosts')
    hosts = [
        {'id': 1, 'event_id': 1, 'user_id': 2},
        {'id': 2, 'event_id': 1, 'user_id': 4},
        {'id': 3, 'event_id': 2, 'user_id': 4},
        {'id': 4, 'event_id': 2, 'user_id': 7},
        {'id': 5, 'event_id': 3, 'user_id': 10},
        {'id': 6, 'event_id': 3, 'user_id': 8},
        {'id': 7, 'event_id': 4, 'user_id': 7},
        {'id': 8, 'event_id': 4, 'user_id': 2},
        {'id': 9, 'event_id': 5, 'user_id': 5},
        {'id': 10, 'event_id': 5, 'user_id': 10},
    ]
    for host in hosts:
        hosts_table.put_item(Item=host)
    logging.info("Seeded event_hosts table.")

# FastAPI event hook

def register_dynamodb_init(app: FastAPI):
    @app.on_event("startup")
    async def startup_event():
        init_dynamodb()
