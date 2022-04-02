# syntax=docker/dockerfile:1

FROM python:3.8-alpine

WORKDIR /app
RUN apk add --no-cache git
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

CMD ["python3", "app.py" ]