import json
import boto3
from botocore.exceptions import ClientError
import time
import datetime
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get parameter
ddb_table = os.environ['DYNAMO_TABLE_NAME']
ddb = boto3.client('dynamodb')

# Query User Id and validate the login ticket

def validate_login_ticket(ddb, ddb_table, pk, sk, login_ticket):
    if not ddb:
        ddb = boto3.client('dynamodb')
    try: 
        logger.info('Query player information from DynamoDB...')
        response =ddb.query(
            TableName = ddb_table,
            Select = 'SPECIFIC_ATTRIBUTES',
            KeyConditionExpression = 'PK = :pk and SK = :sk',
            ExpressionAttributeValues ={
                ':pk' : {'S' : pk},
                ':sk' : {'S' : sk}
            },
            ProjectionExpression = 'loginTicket',
            ReturnConsumedCapacity='TOTAL'
            )
    except ClientError as error:
        logger.exception(error)
        raise error
    else:
      logger.info(response)
      sys_ticket = response['Items'][0]['loginTicket']['S']
      logger.info(sys_ticket)
      validation = sys_ticket == login_ticket
      logger.info('Validation : ' + str(validation))
      return validation 
      
# Update Login Ticket information to DynamoDB
def update_login_info(ddb, ddb_table, pk, sk):
    if not ddb:
        ddb = boto3.client('dynamodb')
    try:
        logger.info('Updating player information to DynamoDB...')
        response = ddb.update_item(
            TableName = ddb_table,
            Key={
                'PK' : {'S' : pk},
                'SK' : {'S' : sk}
            },
            UpdateExpression  = 'SET loginProcessedAt = :t',
            ExpressionAttributeValues = {
                ':t' : {'S' : str(datetime.datetime.utcnow().isoformat())}
            }
        )
    except ClientError as error:
        logger.exception(error)
        raise error
    else:
      logger.info(response)
      return(response)
      
def lambda_handler(event, context):
    i = 0
    for record in event['Records']:
        logger.info("Item#" + str(i))
        body = record['body']
        # print(record['body'])
        # print(type((record['body'])))
        # Decode json string
        d = json.loads(body)
        user_id = d['user_id']
        login_ticket = d['login_ticket']
        pk = 'USER#' + user_id
        sk = 'METADATA#' + user_id
        if validate_login_ticket(ddb, ddb_table, pk, sk, login_ticket):
            update_login_info(ddb, ddb_table, pk, sk)
            logger.info('Ticket validation success, UserID :' + user_id + 'Ticket#' + login_ticket)
        else:
            logger.info('Ticket validation failed, UserID :' + user_id + 'Ticket#' + login_ticket)
        time.sleep(5)
        i += 1