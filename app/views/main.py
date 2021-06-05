import jwt
from flask import Blueprint, request, render_template

from app import JWT_SECRET, db, CLIENT_ID, CALLBACK_URL

bp = Blueprint(
    'main',
    __name__,
    url_prefix='/',
)


@bp.route('', methods=['GET'])  # 데코레이터 문법
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


# 네아로 콜백
@bp.route('/naver', methods=['GET'])
def callback():
    # CLIENT_ID = os.environ['CLIENT_ID']
    # CALLBACK_URL = os.environ['CALLBACK_URL']

    return render_template('callback.html', CALLBACK_URL=CALLBACK_URL, CLIENT_ID=CLIENT_ID)


@bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@bp.route('/register', methods=['GET'])
def register():
    return render_template('register.html')
