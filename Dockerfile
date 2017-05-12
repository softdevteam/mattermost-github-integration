FROM jfloff/alpine-python:2.7

# for a flask server
EXPOSE 5000

# to copy the python files 
COPY . ./
RUN mv config.template config.py
RUN pip install flask
RUN pip install requests
CMD python server.py
