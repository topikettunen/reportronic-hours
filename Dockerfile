FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    firefox \
    python3 \
    python3-pip \
    xvfb \
    curl \
    wget

RUN mkdir app

COPY config.json /app/

COPY requirements.txt /app/
COPY reportronic-hours.py /app/
COPY utils/xvfb-run-script.sh /app/
RUN chmod +x /app/xvfb-run-script.sh

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.22.0/geckodriver-v0.22.0-linux64.tar.gz

RUN tar -xvzf geckodriver-v0.22.0-linux64.tar.gz
RUN mv geckodriver /usr/bin/

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN mkdir /app/pics

ENTRYPOINT [ "/app/xvfb-run-script.sh" ]
