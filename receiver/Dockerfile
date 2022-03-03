FROM ubuntu:18.04
LABEL maintainer="mjantsan@bcit.ca"

RUN apt-get update -y && apt-get install -y python3 python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 9070

ENTRYPOINT [ "python3" ]

CMD ["app.py"]