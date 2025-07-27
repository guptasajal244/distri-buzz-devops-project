FROM python:3.9-slim-buster AS builder

WORKDIR /app

COPY /requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim-buster

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

EXPOSE 5001

CMD ["gunicorn","--bind","0000:5001","app:app"]



