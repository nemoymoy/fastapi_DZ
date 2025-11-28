FROM python:3.12-alpine

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./app /app
WORKDIR /app
ENTRYPOINT ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]