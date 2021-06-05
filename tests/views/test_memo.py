import datetime

import jwt

from tests.conftest import db


def test_메모장_저장(client):
    # 테스트용 메모
    # 실제 네이버 서버를 호출하지 않는 mocking 문법
    url = 'https://news.naver.com/main/read.nhn?mode=LSD&mid=shm&sid1=104&oid=421&aid=0005365428'
    comment = 'test comment'

    data = {
        'url_give': url,
        'comment_give': comment,
    }

    # 임의 사용자 만들기
    expiration_time = datetime.timedelta(hours=1)
    payload = {
        'id': 'test',
        'exp': datetime.datetime.utcnow() + expiration_time

    }
    token = jwt.encode(payload, 'secret')
    headers = {
        'authorization': f'Bearer {token}'

    }

    response = client.post(
        '/memo',
        data=data,
        headers=headers
    )

    assert response.status_code == 200

    # mongodb저장되었는지 확인
    memo = db.articles.find_one(
        {'id': 'test'}
    )

    assert memo['comment'] == comment
