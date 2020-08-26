from python:3.8-alpine

RUN apk add --no-cache openssl-dev libffi-dev build-base bash unzip
RUN mkdir app
WORKDIR app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

RUN bash build.sh
RUN cp instance/config.py.sample instance/config.py
ENV FLASK_ENV=production
CMD gunicorn -b 127.0.0.1:5000 -w $GUNICORN_WORKER_COUNT "vulnerable_people_form:create_app(None)"
