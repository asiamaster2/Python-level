These scripts are what I created with Python.

##### List

1. k8s-monitoring-influxd-to-es6
- This is the script to collect the mectrs what stored in InfluxDB by Heapster and send it to Elasticsearch by using the API.
- It script is run as a pod so there are some files to build docker image and deploy it on Kubernetes.
- The credential is stored in the file crypted(by secret).

2. check-data-steam
- This is the script to check the payment status from Steam with the IDs.

3. zabbix-to-es6
- This is the script to collect the values from Zabbix database(MariaDB) and send to Elasticsearch.
- This script is run as daemon with systemd.

4. zabbix
- This is the script to create a screen per host items or host graph per host - API
