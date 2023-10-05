FROM python:3.10-alpine

COPY . /app
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

CMD [ "python", "app.py" ]