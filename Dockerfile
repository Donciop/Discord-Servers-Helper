FROM python:3.9

WORKDIR /discord_bot

ENV ALPHATOKEN=PLACEHOLDER
ENV APIKEYTFT=PLACEHOLDER
ENV MONGOURL=mongodb+srv://DzonyMongony:DzonyBravo12345@creamdatabase.pju7t.mongodb.net/Discord_Bot_Database
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /discord_bot

RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y vim
RUN pip install --upgrade nextcord yt-dlp

COPY . /discord_bot

CMD ["python3.9", "main.py"]


