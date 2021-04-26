import json
import logging
import uuid
import os
import boto3
from botocore.exceptions import ClientError
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Update Login Ticket information to DynamoDB
def update_login_info(user_id, ticket):
    # Get Parameters
    ddb_table = os.environ['DYNAMO_TABLE_NAME']
    
    # Get DynamoDB service client
    ddb = boto3.client('dynamodb')

    try:
        logger.info('Updating player information to DynamoDB...')
        pk = 'USER#' + user_id
        sk = 'METADATA#' + user_id
        response = ddb.update_item(
            TableName = ddb_table,
            Key={
                'PK' : {'S' : pk},
                'SK' : {'S' : sk}
            },
            UpdateExpression  = 'SET loginTicket = :l',
            ExpressionAttributeValues = {
                ':l' : {'S' : ticket}
            }
        )
    except ClientError as error:
        logger.exception(error)
        raise error
    else:
      logger.info(response)
      return(response)

# Send Ticket to SQS
def send_message(msg_body, msg_attributes=None):
    if not msg_attributes: 
        msg_attributes={}
    # Get the service resource
    sqs = boto3.client('sqs')
    url = os.environ['QUEUE_URL']

    # Create and send message
    try: 
        logger.info('Sending LoginTicket to SQS...')
        msg_response = sqs.send_message(
            QueueUrl=url,
            MessageBody=msg_body,
            MessageAttributes=msg_attributes
        )
        
        attr_response = sqs.get_queue_attributes(
            QueueUrl=url,
            AttributeNames=['ApproximateNumberOfMessages', 'ApproximateNumberOfMessagesNotVisible']
        )
        appr_msg_1 = int(attr_response['Attributes']['ApproximateNumberOfMessages'])
        appr_msg_2 = int(attr_response['Attributes']['ApproximateNumberOfMessagesNotVisible'])
    except ClientError as error:
        logger.exception("Send Message failed: %s", msg_body)
        raise error
    else:
        logger.info(msg_response)
        return appr_msg_1 + appr_msg_2

def lambda_handler(event, context):
    try:
        #Get user_id from requestContexts
        user_id = event['requestContext']['authorizer']['claims']['sub']
        logger.info('UserID :' + user_id)
        #Generate login ticket
        login_ticket = str(uuid.uuid1())
        logger.info('Ticket :' + login_ticket)
        
        #Create message body
        msg_body = json.dumps(
            {
                "user_id": user_id,
                "login_ticket": login_ticket
            }
        )
    
       
        update_login_info(user_id, login_ticket)
        q_len = send_message(msg_body)
        
        return {
            'statusCode': 200,
            'body': json.dumps(
                {
                'ticket':login_ticket,
                'sqs_length' : q_len
                }
            )
        }
    #Catch error
    except Exception as ex:
        logger.exception("[Error] %s", ex)

        return {
            "statusCode" : 500,
            "body": "Internal server error"
        }