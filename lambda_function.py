import requests
import json
import os
import logging
import random
import boto3 

#Region指定しないと、デフォルトのUSリージョンが使われる
clientLambda = boto3.client('lambda', region_name='ap-northeast-1')

#push messageを送信する場合は1、レシピを単に返す場合は0
PUSH_SWITCH = os.environ.get("PUSH_SWITCH")

#api呼び出し時の引数取得
application_id = os.environ.get('RAKUTEN_APPID')
CATEGORY_LIST = ["30","31","32","36","37","38","39","14","15"]

#logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('Loading function')

def lambda_handler(event, context):

    # lineのメッセージにレシピが入っていない場合は終了
    lineText = event["lineMessage"]["events"][0]["message"]["text"]
    logger.info(lineText)
    if "レシピ" not in lineText :
        return None
    
    # category_idをLISTからランダムに取得し、レシピデータ取得
    category_id = random.choice(CATEGORY_LIST)
    recipes = get_recipes(application_id, category_id)
    
    # 複数のレシピデータから今日のレシピを選択し、メッセージを整形
    todays_recipe = random.choice(recipes["result"]) 
    recipe_title = todays_recipe["recipeTitle"] 
    recipe_url = todays_recipe["recipeUrl"]
    message = recipe_title +"はいかがですか？"+"\n詳細は "+recipe_url
    
    # PUSH_SWITCHが1の場合のみ、配信先ユーザーリストを取得し、全ユーザーにメッセージをプッシュ
    if PUSH_SWITCH == "1":
        user_list = get_user_list()
        for user_id in user_list:
            logger.info(user_id)
            push_message(user_id,message)
        return None
    else: 
    # messageを返す    
        return { "message" : message }
    
    
def push_message(user_id,message):
    clientLambda.invoke(
        #pushMessageサービスを呼び出し
        FunctionName='cloud9-pushMessage-pushMessage-QFAN7KZ9AW5U',
        # RequestResponse = 同期、Event = 非同期 で実行できます
        InvocationType='RequestResponse',
        # byte形式でPayloadを作って渡す
        Payload=json.dumps( {"to": user_id, "messages": {"type": "text", "text": message}}).encode("UTF-8")
    )


def get_user_list():
    response = clientLambda.invoke(
        #storageGetサービスを呼び出し
        FunctionName = 'cloud9-storageDao-storageGet-SV2WOCWTIT0Z',
        # RequestResponse = 同期、Event = 非同期 で実行できます
        InvocationType = 'RequestResponse',
        LogType = "Tail",
        # byte形式でPayloadを作って渡す
        Payload = json.dumps({"key":"recipe_user_list"}).encode("UTF-8")
    )
    user_list = json.loads(response['Payload'].read().decode())
    logger.info(user_list)
    return user_list

        
def get_recipes(application_id, category_id):
    url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426'
    payload = {
        'applicationId': application_id,
        'categoryId': category_id
        }
    r = requests.get(url, params=payload)
    logger.info(r)
    response = r.json()
    return response