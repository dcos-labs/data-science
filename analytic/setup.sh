#!/usr/bin/env bash

if [ "$1" == "" ]; then
    echo "No Load Balancer URL provided"
    exit 1
fi

cp -R redash_json/ /tmp/
sed -i "s/ELB/$1/" /tmp/redash_json/jupyterlab.json
sed -i "s/ELB/$1/" /tmp/redash_json/redashserver.json

dcos package install marathon-lb --yes
dcos package install hdfs --yes
dcos package install spark --yes
dcos package install cockroachdb --yes
dcos package install jupyterlab --options=/tmp/redash_json/jupyterlab.json --yes
dcos marathon app add /tmp/redash_json/redis.json
sleep 10
dcos marathon app add /tmp/redash_json/postgres.json
sleep 10
dcos marathon app add /tmp/redash_json/redashserver.json
sleep 10
dcos marathon app add /tmp/redash_json/redashworker.json
sleep 10
dcos marathon app add /tmp/redash_json/redashscheduler.json

export C_TASK=`dcos task | grep cockroachdb-0 | awk '{print $5}'`
cat create_cockroach_db.sql | dcos task exec --interactive $C_TASK cockroach sql --insecure
