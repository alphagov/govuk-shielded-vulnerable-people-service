from python:3.8-slim-buster

RUN apt update
RUN apt install -y libssl-dev libffi-dev  bash unzip
RUN mkdir app
WORKDIR app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENV FLASK_ENV=development
ENV FLASK_CONFIG_FILE='config.py'
ENV FLASK_APP='run.py'
ENV GUNICORN_WORKER_COUNT=4

CMD flask run --host 0.0.0.0
