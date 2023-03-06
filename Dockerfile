FROM python:3.9

WORKDIR /discord_bot

ENV APIKEYTFT=RGAPI-f6cda379-2634-455d-804f-de7c412cd1e8
ENV MONGOURL=mongodb+srv://DzonyMongony:DzonyBravo12345@creamdatabase.pju7t.mongodb.net/Discord_Bot_Database
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /discord_bot

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /discord_bot

CMD ["python3.9", "main.py"]


