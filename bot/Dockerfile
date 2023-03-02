FROM python:3.8.6

RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean

RUN mkdir /bot
COPY . /bot
WORKDIR /bot
VOLUME /opt/app/data
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "app.py"]