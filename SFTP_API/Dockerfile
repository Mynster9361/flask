FROM python:3-slim

RUN apt-get update && \
    apt-get install -y python3 python3-pip

COPY ./src /app/src
COPY ./requirements.txt /app

WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host=0.0.0.0", "--reload"]
