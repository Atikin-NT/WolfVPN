FROM python:3.10-alpine

COPY . /app
COPY config.ini /app/config.ini
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "debit.py"]