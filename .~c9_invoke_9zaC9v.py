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
    # TODO implementz
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
    response_message = recipe_title +"はいかがですか？"+"\n詳細は "+recipe_url
    return { "message" : response_message }