import datetime
import hashlib

import jwt
from flask import Blueprint, request, jsonify
from app import db, JWT_SECRET

bp = Blueprint(
    'api',  # 블루프린트 이름
    __name__,  # 파일 등록(현재 파일)
    url_prefix='/api',  # 패스 접두사
)


@bp.route('/register', methods=['POST'])
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

    # 네이버 가입 API
    @bp.route('/register/naver', methods=['POST'])
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


@bp.route('/login', methods=['POST'])
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
