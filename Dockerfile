# syntax=docker/dockerfile:1

FROM python:3.7

WORKDIR /app

COPY requierements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

CMD ["python3", "app.py" ]