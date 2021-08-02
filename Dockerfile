FROM python:3.8-slim

ENV NO_LOG_FILE=Yes
ENV TZ=Asia/Taipei

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]