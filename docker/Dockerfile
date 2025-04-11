FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python3 -c "from database import init_db; init_db()"

CMD ["python3", "bot.py"]
