import boto3
from botocore.exceptions import ClientError
import datetime
import time
import logging
import uuid
import json
import os
import random
import string

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# DDB put function
def put_player_data(ddb, ddb_table, pk, sk, login_ticket, email):
    if not ddb :
        ddb = boto3.client('dynamodb')
    try:
        logger.info('Putting login information to DynamoDB...')
        iso_ts = str(datetime.datetime.utcnow().isoformat())
        ts = str(int(time.time()))
        response = ddb.put_item(
            TableName = ddb_table,
            Item={
                'PK': {'S': pk},
                'SK': {'S': sk},
                'createdAt' : {'S' : iso_ts },
                'loginTicket' : {'S': login_ticket},
                'email' : {'S': email},
                'ttl' : {'N' : ts }
            }
        )
    except ClientError as error:
        logger.exception("Put Item failed: %s", pk)
        print('Exception during DDB input')
        raise Exception
    else:
        return response

# SQS send message
def send_message(sqs, url, msg_body, msg_attributes=None):
    if not msg_attributes: 
            msg_attributes={}
    try: 
        logger.info('Sending LoginTicket to SQS...')
        response = sqs.send_message(
            QueueUrl=url,
            MessageBody=msg_body,
            MessageAttributes=msg_attributes
        )
    except ClientError as error:
        logger.exception("Send Message failed: %s", msg_body)
        print("Exception during sending message to SQS")
        raise error
    else:
        logger.info(response)
        return response

def lambda_handler(event, context):
    ddb = boto3.client('dynamodb')
    sqs = boto3.client('sqs')
    
    ddb_table = os.getenv('DYNAMO_TABLE_NAME')
    url = os.getenv('SQS_URL')
    iteration = int(os.getenv('ITERATION'))
    
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(6))
    
    for i in range(iteration):
        # Generate random user id
        user_id = str(uuid.uuid1())

        # Construct DDB primary key
        pk = 'USER#' + user_id
        sk = 'METADATA#' + user_id
        email = result_str + str(i) + '@gmotest.com'
        
        try:
            #Generate login_ticket
            login_ticket = str(uuid.uuid1())
            logger.info('Ticket :' + login_ticket)

            put_player_data(ddb, ddb_table, pk, sk, login_ticket, email)

            #Create message body
            msg_body = json.dumps(
                {
                    "user_id": user_id,
                    "login_ticket": login_ticket
                }
            )
            send_message(sqs, url, msg_body)
        except:
                return {
                'statusCode': 500,
                'body': json.dumps('Internal Server Error')
                }
                raise Exception
    return {
        'statusCode': 200,
        'body': json.dumps('Load generation loop completed')
    }
