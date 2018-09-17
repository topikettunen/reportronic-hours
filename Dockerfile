FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    xvfb \
    curl

RUN mkdir app

COPY config.json /app/

# Remove in prod.
COPY config-test.json /app/

COPY requirements.txt /app/
COPY reportronic-hours.py /app/
COPY run-script.sh /app/

WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "/app/run-script.sh" ]
