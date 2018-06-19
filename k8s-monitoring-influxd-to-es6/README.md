This is the script to collect the metrics stored by Heapster from Influxdb and send it to Elasticsearch6

pip:
- requests
- influxdb
- elasticsearch

##### Installation
There is nothing dependency.
Just execute heapster-elasticsearch.py.

##### Configuration

```

LOCKFILE_LOCATION = "./sciprtisrunning"

# buffer size
buffsize = 5000

# Configuration for influxDB
USER = 'USERID'
PASSWORD = 'THEPASSWORD'
DBNAME = 'k8s'
host = 'monitoring-influxdb.default.svc'
port = 8086
client = InfluxDBClient(host, port, USER, PASSWORD, DBNAME)

# Configuration for ES6
esport = 9200
esindex = 'IDEXNAME-' + date.today().strftime("%Y.%m.%d")
estype = 'log'
# es= Elasticsearch([{'host': eshost, 'port': esport, }])
es = Elasticsearch(['es02.URL', 'es03.URL', 'es04.URL', 'es01.URL'],
                   port=esport,
                   )


# Change this to yes if you want to send the node metrics as well.
nodedata = 'no'



```
