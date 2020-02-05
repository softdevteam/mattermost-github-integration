FROM jfloff/alpine-python:latest

RUN apk add --update jpeg-dev zlib-dev

# for a flask server
EXPOSE 5000

COPY requirements.txt /root/requirements.txt
RUN pip install -r /root/requirements.txt
RUN pip install gunicorn
CMD gunicorn -b 0.0.0.0:5000 mattermostgithub:app
