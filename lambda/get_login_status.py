import json
import logging
import os
import boto3
from botocore.exceptions import ClientError
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get parameter
ddb_table = os.environ['DYNAMO_TABLE_NAME']
ddb = boto3.client('dynamodb')

def check_login_status(ddb, user_id, login_ticket):
    if not ddb :
        ddb = client.boto3('dynamodb')
    pk = 'USER#' + user_id
    sk = 'METADATA#' + user_id
    try: 
        response =ddb.get_item(
            TableName = ddb_table,
            Key = {
                'PK' : {'S' : pk},
                'SK' : {'S' : sk}
            },
            ProjectionExpression = 'loginProcessedAt, loginTicket',
            ReturnConsumedCapacity='TOTAL'
            )
        print(response['Item'])
        if not response['Item']['loginTicket']['S'] == login_ticket:
            logger.exception('Invalid Ticket')
            raise Exception('Invalid Ticket')
        elif response['Item'].get('loginProcessedAt') is None:
            logger.info('Still waiting...')
            login_status = False
            return login_status
        else :
            logger.info('Login processed at :' + response['Item']['loginProcessedAt']['S'])
            login_status = True
            return login_status
    except ClientError as error:
        print(error)
    except Exception as e:
        print('Exception :', e)

def lambda_handler(event, context):
    try:
        #Get user_id from requestContexts
        user_id = event['requestContext']['authorizer']['claims']['sub']
        logger.info('UserID :' + user_id)
        
        #Get login ticket from query parameter
        login_ticket= event['queryStringParameters']['login_ticket']
        logger.info(login_ticket)
        
        #Get user's login status
        login_status = check_login_status(ddb, user_id, login_ticket)
        
        #Create message body
        msg_body = json.dumps(
            {
                'login_ticket': login_ticket,
                'login_status': login_status
            }
        )
        return {
            'statusCode': 200,
            'body': msg_body
        }
    except:
        return {
            'statusCode': 500,
            'body': 'Internal Server Error'
        }
