FROM python:3.10-alpine

COPY . /app
COPY config.ini /app/config.ini
COPY ./requirements.txt /app/requirements.txt
COPY ./ssl.crt /app/ssl.crt
COPY ./ssl.key /app/ssl.key

WORKDIR /app

RUN apk update && apk add python3-dev \
                        gcc \
                        libc-dev \
                        build-base \ 
                        linux-headers

RUN pip install -r requirements.txt

CMD ["gunicorn", "--ssl-version", "TLSv1_3", "--certfile", "ssl.crt", "--keyfile", "ssl.key", "-b", "0.0.0.0:8443", "--workers", "1", "app:app", "--log-file", "app.log", "--log-level", "debug", "-c", "gunicorn.conf.py"]