FROM python:3.11-alpine

WORKDIR /app

RUN apk --no-cache add git

COPY . .

RUN pip install -r requirements.txt

ENV PORT=3001
ENV BACKEND_URL="localhost:8000"

EXPOSE ${PORT}

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
