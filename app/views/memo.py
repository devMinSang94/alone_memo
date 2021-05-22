import jwt
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, request, jsonify

from app import JWT_SECRET, db

bp = Blueprint(
    '/memo',
    __name__,
    url_prefix='/memo'
)


# 아티클 추가 api
@bp.route('', methods=['POST'])
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

    @bp.route('', methods=['GET'])
    def list_memo():
        memos = list(db.articles.find({}, {'_id': 0}))
        result = {
            'result': 'success',
            'articles': memos,
        }
        return jsonify(result)
