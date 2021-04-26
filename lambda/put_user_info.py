import os
import json
import boto3
from botocore.exceptions import ClientError
import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get parameter
ddb_table = os.environ['DYNAMO_TABLE_NAME']

# import requests
def put_user_metadata(user_info):
    ddb = boto3.client('dynamodb')
    
    pk = 'USER#' + user_info[0]
    sk = 'METADATA#' + user_info[0]
    
    try:
        logger.info('Putting login information to DynamoDB...')

        response = ddb.put_item(
            TableName = ddb_table,
            Item={
                'PK': {'S': pk},
                'SK': {'S': sk},
                'createdAt' : {'S' : str(datetime.datetime.utcnow().isoformat())},
                'email' : {'S' : user_info[1]}
            }
        )
    except ClientError as error:
        logger.exception("Put Item failed: %s", user_info[1])
        raise error
    else:
      logger.info(response)
      
def lambda_handler(event, context):
    try:
        #Get user_info from requestContexts and store to list
        user_info =[]
        user_info.append(event['request']['userAttributes']['sub']) 
        user_info.append(event['request']['userAttributes']['email']) 
        
        #Create new user item in DynamoDB
        put_user_metadata(user_info)
        
        return event
    #Catch error
    except Exception as ex:
        logger.exception("[Error] %s", ex)
        
        return event