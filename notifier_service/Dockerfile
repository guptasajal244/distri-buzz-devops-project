FROM python:3.9-slim-buster AS builder

WORKDIR /app

COPY /requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim-buster

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/
COPY . .

EXPOSE 5003

CMD ["gunicorn","--bind","0000:5003","app:app"]


