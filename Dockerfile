FROM python:3.6-stretch

RUN apt update -y && apt install -y libpq-dev python3-dev build-essential

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD python ./post-alert-bot/bot.py