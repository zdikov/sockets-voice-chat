FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-pyaudio
COPY . .
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3", "server.py"]

