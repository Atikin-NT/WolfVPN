FROM python:3.10-alpine

COPY . /app
COPY config.ini /app/config.ini
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN apk update && apk add python3-dev \
                        gcc \
                        libc-dev \
                        build-base \ 
                        linux-headers

RUN pip install -r requirements.txt

CMD [ "python", "app.py" ]