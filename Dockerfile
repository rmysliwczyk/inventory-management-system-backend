FROM python:3.13-slim-trixie

WORKDIR /

COPY ./app /app
COPY ./.env /.env
COPY ./requirements.txt /requirements.txt

RUN pip install -r requirements.txt

CMD [ "fastapi", "run", "--host", "0.0.0.0", "--port", "8004" ]
