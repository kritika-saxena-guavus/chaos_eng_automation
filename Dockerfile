FROM artifacts.ggn.in.guavus.com:4244/python:3.7-alpine-nimble
WORKDIR /automation/
RUN apk add freetype-dev jpeg-dev
RUN pip install --no-cache-dir "chaostoolkit-nimble==0.0.2" --extra-index-url http://192.168.192.201:5050/simple/ --trusted-host 192.168.192.201
