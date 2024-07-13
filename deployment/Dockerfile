FROM python:3.11-slim

COPY . /app

WORKDIR /app

RUN pip install pipenv
RUN pipenv install --system --deploy

EXPOSE 8080

CMD python -m deployment.main
