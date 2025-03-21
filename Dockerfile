FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "3000", "--reload"]
