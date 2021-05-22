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


# 플라스크 프레임워크에서 지정한 함수 이름
# 플라스크 동작시킬떄 create_app() 함수의 결과로 리턴한 앱을 실행시킨다.
def create_app():
    app = Flask(__name__)

    # mongodb 추가
    client = MongoClient('localhost', 27017)
    db = client.get_database('sparta')

    # .env 파일을 환경변수로 설정
    load_dotenv()
    # 환경변수 읽어오기
    JWT_SECRET = os.environ['JWT_SECRET']

    # API 추가
    @app.route('/', methods=['GET'])  # 데코레이터 문법
    def index():  # 함수 이름은 고유해야 한다
        token = request.cookies.get('loginToken')
        print(token)
        if token:
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                print(payload)
                memos = list(db.articles.find({'id': payload['id']}, {'_id': False}))
            except jwt.ExpiredSignatureError:
                memos = []
        else:
            memos = []
        return render_template('index.html', test='테스트', memos=memos)

    # 아티클 추가 api
    @app.route('/memo', methods=['POST'])
    def save_memo():
        form = request.form
        url_receive = form['url_give']
        comment_receive = form['comment_give']

        # JWT 추출
        token_receive = request.headers['authorization']
        token = token_receive.split()[1]
        print(token)

        # JWT 페이로드에서 id 확인
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        id = payload['id']

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        response = requests.get(
            url_receive,
            headers=headers

        )

        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.select_one('meta[property="og:title"]')
        url = soup.select_one('meta[property="og:url"]')
        image = soup.select_one('meta[property="og:image"]')
        description = soup.select_one('meta[property="og:description"]')

        print(title['content'])
        print(url['content'])
        print(image['content'])
        print(description['content'])

        print(url_receive, comment_receive)
        document = {
            'title': title['content'],
            'url': url['content'],
            'image': image['content'],
            'description': description['content'],
            'comment': comment_receive,
            'id': id,
        }
        db.articles.insert_one(document)

        return jsonify(
            {'result': 'success', 'msg': '저장했습니다.'}
        )

    @app.route('/memo', methods=['GET'])
    def list_memo():
        memos = list(db.articles.find({}, {'_id': 0}))
        result = {
            'result': 'success',
            'articles': memos,
        }
        return jsonify(result)

    @app.route('/login', methods=['GET'])
    def login():
        CLIENT_ID = os.environ['CLIENT_ID']
        CALLBACK_URL = os.environ['CALLBACK_URL']
        SERVICE_URL = os.environ['SERVICE_URL']
        print(CLIENT_ID, CALLBACK_URL, SERVICE_URL)
        return render_template('login.html', CLIENT_ID=CLIENT_ID, CALLBACK_URL=CALLBACK_URL, SERVICE_URL=SERVICE_URL)

    @app.route('/register', methods=['GET'])
    def register():
        return render_template('register.html')

    @app.route('/api/login', methods=['POST'])
    def api_login():
        id = request.form['id_give']
        pw = request.form['pw_give']
        # TODO id , pw 검증 후에 JWT 만들어서 리턴

        pw_hash = hashlib.sha256(pw.encode()).hexdigest()

        user = db.users.find_one({'id': id, 'pw': pw_hash})

        # 만약 가입했다면
        if user:
            # 로그인 성공이기 떄문에 JWT 생성
            expiration_time = datetime.timedelta(hours=1)
            payload = {
                'id': id,
                'exp': datetime.datetime.utcnow() + expiration_time,  # 발급시간으로부터 1시간 동안 jwt가 유효하다.
            }
            token = jwt.encode(payload, JWT_SECRET)
            print(token)

            return jsonify({'result': 'success', 'token': token})
        # 가입하지 않은 상태
        else:
            return jsonify({'result': 'fail', 'msg': '로그인실패'})

    # 네아로 콜백
    @app.route('/naver', methods=['GET'])
    def callback():
        CLIENT_ID = os.environ['CLIENT_ID']
        CALLBACK_URL = os.environ['CALLBACK_URL']

        return render_template('callback.html', CALLBACK_URL=CALLBACK_URL, CLIENT_ID=CLIENT_ID)

    # 네이버 가입 API
    @app.route('/api/register/naver', methods=['POST'])
    def api_register_naver():
        naver_id = request.form['naver_id']
        print(naver_id)

        # 아직 가입하지 않은 naver id 케이스에서는 가입까지 처리
        if not db.users.find_one({'id': naver_id}):
            db.users.insert_one({'id': naver_id, 'pw': ''})

        expiration_time = datetime.timedelta(hours=1)
        payload = {
            'id': naver_id,
            # jwt 유효기간 - 이 시간 이후에는 jwt 인증이 불가능 합니다.
            'exp': datetime.datetime.utcnow() + expiration_time
        }
        token = jwt.encode(payload, JWT_SECRET)

        return jsonify({'result': 'success', 'token': token})

    @app.route('/api/register', methods=['POST'])
    def api_register():
        id = request.form['id_give']
        pw = request.form['pw_give']

        # salting
        # pw + 랜덤 문자열 추가 (솔트)
        # 솔트 추가된 비밀번호를 해시
        # DB에 저장할 떄는 (해시 결과물 + 적용할 솔트) 묶어서 적용

        # 회원가입
        pw_hash = hashlib.sha256(pw.encode()).hexdigest()
        db.users.insert_one({'id': id, 'pw': pw_hash})
        return jsonify({'result': 'success'})

        # app.py 파일을 직접 실행시킬 떄 동작시킴

    @app.route('/user', methods=['POST'])
    def user_info():
        token_receive = request.headers['authorization']
        print(token_receive)
        token = token_receive.split()[1]
        print('token:', token)

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            print('payload:', payload)
            return jsonify({'result': 'success', 'id': payload['id']})
        except jwt.exceptions.ExpiredSignatureError:
            # try 부분을 실행했지만 위와 같은 에러가 난다면
            return jsonify({'result': 'fail'})

    @app.route('/delete', methods=['POST'])
    def delete_user():
        id = request.form['id']
        print(id)
        if db.users.find({'id': id}) == id:
            db.users.delete({'id': id})
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'fail'})

    return app
