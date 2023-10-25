FROM python:3.10-alpine

COPY . /app
COPY ./requirements.txt /app/requirements.txt
COPY ./ssl.crt /app/ssl.crt
COPY ./ssl.key /app/ssl.key

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["gunicorn", "--certfile", "ssl.crt", "--keyfile", "ssl.key", "-b", "0.0.0.0:443", "app:app"]
