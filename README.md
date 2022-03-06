# Simple voice chat based on sockets

## How to run server?
```sh
docker run -p 8080:<your_port> zdikov/sockets-voice-chat-server
```
## How to run client?

### Install requirements
#### Ubuntu
```sh
apt update
apt install python3-pip python3-pyaudio
pip3 install -r requirements.txt
```
#### MacOS using `brew`
```sh
brew install python3 portaudio
pip3 install -r requirements.txt
```
### Run client
```sh
python3 client.py
```
