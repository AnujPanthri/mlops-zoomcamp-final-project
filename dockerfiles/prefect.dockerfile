FROM python:3.11-slim

RUN apt-get update
RUN pip install -U prefect==2.19.7
