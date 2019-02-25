# Analytic Reporting

This repo is meant to set up and run a demo for working with streaming data and an RDBMS. This example mimics data streaming from HDFS to Cockroach DB. Reports are built against Cockroach using Redash.

## Prerequisites

It is assumed that you already have a DCOS cluser up and running with the dcos client installed locally and configured to reach the cluster. The cluster must have at least one public accessable node for the load balancer to attach.


## Getting Started

Determine the plublic agent URL. If using our terraform method to install the cluser, the URL required is the "Public Agent ELB Public IP":
<br> e.g.

```
Public Agent ELB Public IP = XXX-pub-agt-elb-XXX-elb.amazonaws.com
```

### Installing

Run the setup script and provide the public agent url.

```
./setup.sh <Public Agent URL>
```

This will install many components:
* marathon-lb
* hdfs
* spark
* Jupyter Lab
* cockroachdb
  * Create tx database
  * Create kickstart table in tx database
* Redash
  * Redis
  * Postgres database for Redash internals
  * Redash Server
  * Redash Worker
  * Redash scheduler


## Setup inside Jupyter
Open Jupyter Lab
```
http://<marathon-lb url>/jupterlab-notebook
```

Clone this git repo inside the JupyterLab container:
```
git clone https://github.com/dcos-labs/data-science.git
```

Get the Cockroach DB endpoint from the services tab in the web interface or using the command line:
```
dcos cockroachdb endpoints pg
```

```
# Set the endpoint IP
# Default port is assumed
COCKROACH_ENDPOINT=''
conda create --yes -n Data python=3.6 sqlalchemy ipykernel
source activate Data
python -m ipykernel install --user --name=Data
conda install --yes psycopg2 pandas seaborn
~/data-science/load_cockroach.py $COCKROACH_ENDPOINT
```

### Test connection with Jupyter Notebook
Run through readDB.ipynb

### Test Redash
Open Redash installed as the default app on the load balancer.
```
http://<marathon-lb url>
```
* Create Connection using endpoint data
  * Host is Cockroach DB (PG Endpoint)
  * Port: 26257
  * User: test_user
  * Database Name: tx
* Create reports. Example queries in sql directory.
  * backer_pledge_per_month.sql
  * world_map.sql
  * backer_per_category_per_month.sql
  * success_rate_per_category.sql

