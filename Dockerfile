FROM jfloff/alpine-python:2.7

# for a flask server
EXPOSE 5000

RUN pip install -r requirements.txt

CMD python server.py
