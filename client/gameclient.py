from time import sleep
from pyfiglet import Figlet
from authentication import Cognito
import requests
import os
from dotenv import load_dotenv
load_dotenv()

def draw_stickman():
    os.system('clear')
    f = Figlet(font='big')
    print(f.renderText('- - - - - - -'))
    print(f.renderText('     AWSome\n          Game'))
    print(f.renderText('- - - - - - -\n'))
    print('You are In AWSome Game World ')
    to_draw = [
        [" ", "O"],
        # [" ", "|"],
        ["\\", " ", "/"],
        [" ", "|"],
        # [" ", "|"],
        ["/", " ", "\\"]
    ]
    for each_list in to_draw:
        print(''.join(each_list))


def awsomegame_sign_up():
    f = Figlet(font='big')
    print(f.renderText('- - - - - - -'))
    print(f.renderText('     AWSome\n          Game'))
    print(f.renderText('- - - - - - -\n'))

    print('*************************************************************\n')
    print('                       Please sign up                         \n' )
    print('*************************************************************\n')

    # Get User credential from input
    username = input('Username : ')
    password = input('Password : ')

    # Register user to Amazon Cognito
    try :
        auth = Cognito()
        user_register_res = auth.sign_up(username, password)

        if user_register_res['ResponseMetadata']['HTTPStatusCode'] == 200 :
            print('User has been succesfully registered. Please check your email and provide verification code')
            confirm_code = input('Verification code : ')
            confirm_res = auth.sign_up_confirm(username, confirm_code)
            if confirm_res['ResponseMetadata']['HTTPStatusCode'] == 200 :
                print('User has confirm. Please Login to AWSomeGame!!')
                os.system('clear')
            else:    
                print('User confirmation has failed. Ask Administrator')
                raise Exception('User confirmation failed')
        else:
            print('User registration has failed. Please try again')
            raise Exception('User registration failed')
    except:
        raise Exception('User registration failed')


def awsomegame_sign_in():
    f = Figlet(font='big')
    print(f.renderText('- - - - - - -'))
    print(f.renderText('     AWSome\n          Game'))
    print(f.renderText('- - - - - - -\n'))

    print('**************************************************************\n')
    print('                            Login                            \n' )
    print('**************************************************************\n')

    # Get User credential from input
    username = input('Username : ')
    password = input('Password : ')

    # Sign in to Cognito
    try :
        auth = Cognito()
        user_signin_res = auth.sign_in(username, password)
        if user_signin_res['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('Authenticated....')
            id_token = user_signin_res['AuthenticationResult']['IdToken']
            rest_endpoint = os.getenv('AWSOMEGAME_REST_ENDPOINT')
            login_endpoint = rest_endpoint + '/login'
            print(login_endpoint)
            #Construct Authorization header 
            headers = {'Authorization': 'Bearer ' + id_token}
            response = requests.get(login_endpoint, headers=headers)
            if response.status_code == 200:
                login_ticket = response.json()['ticket']
                q_len = response.json()['sqs_length']
                timer = int(q_len * 0.001)
                # Construct url and data for 
                status_endpoint = login_endpoint + '/status'
                data = {'login_ticket' : response.json()['ticket']}
                if timer > 0:
                    print(status_endpoint)
                    print('**************************************************************\n')
                    print('                   You are in waiting queue                   \n' )
                    print('**************************************************************\n')
                    while 0 < timer:
                        print('Approximately : ' + str(timer) + ' seconds remaining..',end='\r', flush=True)
                        sleep(0.9)
                        status = requests.get(status_endpoint, headers=headers, params=data).json()
                        if status['login_status']:
                            draw_stickman()
                            break
                        elif timer == 1 and not status['login_status']:
                            timer += 10
                        else:
                            timer -= 1
                else:
                    draw_stickman()
                # status = requests.get(status_endpoint, headers=headers, params=data)
                # print(status.json())
            else:
                raise Exception('Error on getting loging ticket')
    except:
        print('internal server error please try again!')

def main():
    # awsomegame_sign_up()
    awsomegame_sign_in()

if __name__ == '__main__':
    try: 
        main()
    except:
        print('internal server error please try again!')
        raise Exception
    

