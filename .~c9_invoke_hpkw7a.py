import requests
import json
import os
import logging
import random
import boto3 

#Region指定しないと、デフォルトのUSリージョンが使われる
clientLambda = boto3.client('lambda', region_name='ap-northeast-1')

application_id = os.environ.get('RAKUTEN_APPID')
user_id = os.environ.get('USER_ID')
CATEGORY_LIST = ["30","31","32","36","37","38","39","14","15"]

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('Loading function')

def lambda_handler(event, context):
    # -*- coding: utf-8 -*-
    lineText = event["lineMessage"]["events"][0]["message"]["text"]
    logger.info(lineText)
    
    if "レシピ" not in lineText :
        return None
        
    category_id = random.choice(CATEGORY_LIST)
    
    url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426'
     
    payload = {
        'applicationId': application_id,
        'categoryId': category_id
        }
     
    r = requests.get(url, params=payload)
    logger.info(r)
    resp = r.json()
    todays_recipe = random.choice(resp["result"]) 
    recipe_title = todays_recipe["recipeTitle"] 
    recipe_url = todays_recipe["recipeUrl"]
    message = recipe_title +"はいかがですか？"+"\n詳細は "+recipe_url
    
    user_list = get_user_list()
    logger.info(user_list)
    
    push_message(message)
    
    return { "message" : user_list }
    
def push_message(message):
        push_message_service = clientLambda.invoke(
        # Calleeのarnを指定
        FunctionName='cloud9-pushMessage-pushMessage-QFAN7KZ9AW5U',
        # RequestResponse = 同期、Event = 非同期 で実行できます
        InvocationType='Event',
        # byte形式でPayloadを作って渡す
        Payload=json.dumps( {"to": user_id, "messages": {"type": "text", "text": message}}).encode("UTF-8")
    )

def get_user_list():
        user_list = clientLambda.invoke(
        # Calleeのarnを指定
        FunctionName = 'cloud9-storageDao-storageGet-SV2WOCWTIT0Z',
        # RequestResponse = 同期、Event = 非同期 で実行できます
        InvocationType = 'RequestResponse',
    re
        Payload = json.dumps( {key":"菊池"}).encode("UTF-8")
    )
        logger.info(user_list)
        return user_list
        
    