import datetime
import hashlib
import jwt
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import os
# 플라스크 웹 서버 생성하기

from pymongo import MongoClient

# .env 파일을 환경변수로 설정
load_dotenv()
# 환경변수 읽어오기
JWT_SECRET = os.environ['JWT_SECRET']
CLIENT_ID = os.environ['CLIENT_ID']
CALLBACK_URL = os.environ['CALLBACK_URL']
SERVICE_URL = os.environ['SERVICE_URL']
MONGODB_HOST = os.environ['MONGODB_HOST']

# mongodb 추가
client = MongoClient('localhost', 27017)
db = None


# 플라스크 프레임워크에서 지정한 함수 이름
# 플라스크 동작시킬떄 create_app() 함수의 결과로 리턴한 앱을 실행시킨다.
def create_app(database_name='sparta'):
    app = Flask(__name__)
    # app.py 파일을 직접 실행시킬 떄 동작시킴

    # 파이썬 중급 - 전역 변수를 함수 내부에서 수정 가능하게 만듬
    global db
    db = client.get_database(database_name)

    # 순환참조 방지
    from views import api, main, memo, user

    app.register_blueprint(api.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(memo.bp)
    app.register_blueprint(user.bp)

    return app
