This script in this directory is used to create a screen per host or graph at Zabbix.

## The information
Location : No dependency


### How to use
You have to check&change the variable's value if it's necessary.

```
# Configuration for influxDB
usage: zabbix-create-screen.py [-h] [-c COLUMNS] A H N V W

Create Zabbix screen from all of a host Items or Graphs.

positional arguments:
  A           Set the type as "graph" or "host". This script will create
              screen per this value.
  H           Zabbix Host to create screen from
  N           Screen name in Zabbix. Put quotes around it if you want spaces
              in the name.
  V           zabbix username
  W           zabbix password

optional arguments:
  -h, --help  show this help message and exit
  -c COLUMNS  number of columns in the screen (default: 3)

```