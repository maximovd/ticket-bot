FROM python:3.8

LABEL maintainer="bazinga.mail@yandex.ru"

WORKDIR /home

ENV TELEGRAM_TOKEN=""
ENV URL=""
ENV TOKEN=""
ENV proxy_url=""
ENV username=""
ENV password=""


ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY *.py ./
COPY /utils/*.py ./utils/
COPY requirements.txt ./

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "bot.py"]