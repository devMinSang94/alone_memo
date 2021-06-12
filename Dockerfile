FROM python:3.9

# 이미지 빌드 할 떄 컨테이너 내부에서 실행하는 리눅스 명령어
RUN mkdir /alonememo
# 메모장 코드 파일을 모두 컨테이너 내부로 복사
COPY . /alonememo
# 이미지 빌드할 떄 동작하는 폴더 위치
WORKDIR /alonememo
# 컨테이너 내부에서 pip 인스톨
RUN pip install -r requirements.txt
# 컨테이너 실행시킬 떄 실행할 명령어
CMD flask run --host 0.0.0.0 --port 7000
