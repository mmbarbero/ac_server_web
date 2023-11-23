FROM python:3.10.13-slim-bullseye

ENV DB_HOST = "127.0.0.1"
ENV DB_PORT = #PORT
ENV DB_NAME = ''
ENV DB_USER = ''
ENV DB_PASS = ''

ENV UDP_IP = "127.0.0.1"
ENV UDP_PORT = #PORT
ENV UDP_SEND_PORT = #PORT

ENV WEB_IP="127.0.0.1"
ENV WEB_PORT=#PORT


WORKDIR /ac_monitoring
ADD . /ac_monitoring
RUN apt-get update \
    && apt-get -y install libpq-dev gcc
RUN pip install -r requirements.txt
CMD ["python3","main.py"]