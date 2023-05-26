FROM python:3.9-slim-buster
WORKDIR /app
RUN apt-get update && apt-get -y install gcc g++
RUN pip3 install --upgrade pip
COPY . . 
RUN pip3 install -r requirements.txt && \
    chmod +x startup.sh && \
    dpkg -i /app/libjpeg-turbo-official_2.1.5.1_amd64.deb

ENTRYPOINT ["/app/startup.sh"]