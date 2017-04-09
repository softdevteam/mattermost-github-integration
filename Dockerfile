FROM jfloff/alpine-python:2.7

# for a flask server
EXPOSE 5000

ADD requirements.txt \
    config.template \
    payload.py \
    server.py /

RUN mv config.template config.py

RUN pip install -r requirements.txt

CMD python server.py
