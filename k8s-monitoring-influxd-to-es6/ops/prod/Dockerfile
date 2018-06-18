FROM python:2.7

RUN pip install requests
RUN pip install influxdb
RUN pip install elasticsearch

RUN mkdir /usr/local/pythonscript
COPY app/heapster-elasticsearch.py /usr/local/pythonscript/

CMD [ "python", "/usr/local/pythonscript/heapster-elasticsearch.py" ]
