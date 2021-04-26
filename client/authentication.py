import boto3
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
load_dotenv()

class Cognito:
    # def __init__(self, username, password):
    #     self.username = username
    #     self.password = password
    def sign_up(self, username, password):
        try:
            client = boto3.client('cognito-idp')
            response = client.sign_up(
                ClientId=os.getenv('COGNITO_USER_CLIENT_ID'),
                Username = username,
                Password = password
            )
        except ClientError as error:
            print(error)
            raise error
        else:
            return response

    def sign_up_confirm(self, username, confirm_code):
        try:
            client = boto3.client('cognito-idp')
            response = client.confirm_sign_up(
                ClientId = os.getenv('COGNITO_USER_CLIENT_ID'),
                Username = username,
                ConfirmationCode = confirm_code
            )
        except ClientError as error:
            print(error)
            raise error
        else:
            return response

    def sign_in(self, username, password):
        try:
            client = boto3.client('cognito-idp')
            response = client.initiate_auth(
                ClientId = os.getenv('COGNITO_USER_CLIENT_ID'),
                AuthFlow = 'USER_PASSWORD_AUTH',
                AuthParameters = {
                    'USERNAME' : username,
                    'PASSWORD' : password
                }
            )
        except ClientError as error:
            print(error)
            raise error
        else:
            return response