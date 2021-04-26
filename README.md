서버리스 기반의 게임 로그인 큐 구현 하기
======================
# [소개] 
AWS에서 제공하는 서비리스 서비스인 AWS Simple Queue Service(SQS), Amazon DynamoDB, AWS Lambda 와 클라우드 기반의 인증 서비스인 Amazon Cognito를 연계하여 게임 로그인 대기열 구성 해보겠습니다.

## 1. Architecture
![Reference Architecture](https://github.com/Minsukk/aws-game-login/blob/main/images/serverless-login-queue-architecture.png)

****
## 2. 로그인 대기열 구성
### 2.1. 사전 준비 사항
        1. AWS 계정
        2. IAM Role 생성 (필요 권한)
           1. Amazon DynamoDB, Amazon SQS, AWS Lambda 에 대한 권한 추가
        3. Amazon Cognito User Pool 생성 및 앱 클라이언트 등록 
           1. User Pool 생성 [AWS Document](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pool-as-user-directory.html)
           2. 앱 클라이언트 등록 [AWS Document(https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-client-apps.html)]
        4. Amazon DynamoDB 생성 [AWS Console](https://ap-northeast-2.console.aws.amazon.com/dynamodb/home?region=ap-northeast-2#create-table:)
           1. Primary Key 는 Composite Key(Partition Key + Sort Key)를 사용하며, Partition Key는 'PK', Sort Key는 'SK' 로 정의 
           2. 디폴트 세팅으로 생성. 비용 절감이 필요한 경우, 디폴트 생성 체크 박스를 해제하고 Auto scaling 기능 비활성화
        5. Amazon SQS Standard 생성 [AWS Document](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-configure-create-queue.html)
        6. Amazon API Gateway REST 생성 [AWS Document](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-api-as-simple-proxy-for-lambda.html)

### 2.2 AWS Lambda 구성
        1. Amazon Cognito 트리거 함수 - Post Confrimation 으로 등록[AWS Document](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-post-confirmation.html#aws-lambda-triggers-post-confirm-tutorials)
           1. /lambda/put_player_info.py
        2. Amazon API Gateway 트리거 함수 [AWS Document](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-api-as-simple-proxy-for-lambda.html)
           1. /lambda/queue_player_login.py
           2. /lambda/get_login_status.py
           3. (옵션: 부하 발생) /lambda/generate_load.py
           4. 환경 변수 
              1. DYNAMO_TABLE_NAME : Amazon DynamoDB 테이블 명
              2. 'SQS_URL' : Amazon SQS URL 주소
        3. Amazon SQS 트리거 함수 [AWS Document](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs-example.html)
   
### 2.3 Client 실행
```bash
 ______   ______   ______   ______   ______   ______   ______ 
|______| |______| |______| |______| |______| |______| |______|
                                                              
          __          _______                      
         /\ \        / / ____|                     
        /  \ \  /\  / / (___   ___  _ __ ___   ___ 
       / /\ \ \/  \/ / \___ \ / _ \| '_ ` _ \ / _ \
      / ____ \  /\  /  ____) | (_) | | | | | |  __/
     /_/    \_\/  \/  |_____/ \___/|_| |_| |_|\___|
                                                   
                                                   
            _____                      
           / ____|                     
          | |  __  __ _ _ __ ___   ___ 
          | | |_ |/ _` | '_ ` _ \ / _ \
          | |__| | (_| | | | | | |  __/
           \_____|\__,_|_| |_| |_|\___|
                                       
 ______   ______   ______   ______   ______   ______   ______ 
|______| |______| |______| |______| |______| |______| |______|

You are In AWSome Game World 
 O
\ /
 |
/ \
```

        1. Python virtualenv 사용 권장
        2. 필요 Client 패키지 설치 

```bash
$ pip install -r requirements.txt
```

        1. .env 파일 업데이트
           1. COGNITO_USER_CLIENT_ID : Amazon Cognito App Client ID
           2. (옵션) AWSOMEGAME_REST_ENDPOINT : 부하 분산용 Amazon API GW 엔드포인트
        2. Client 실행

```bash
$ python client/gameclient.py
```