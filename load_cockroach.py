#!/usr/bin/env python
"""Driver
This loads data into Cockroach DB.
Script expects Cockroach IP is passed.
"""
import sys
import subprocess
import time
import psycopg2

if len(sys.argv) == 1:
    print('Must pass IP from Cockroach server')
    sys.exit()
else:
    print('Host IP: ' + str(sys.argv[1]))

subprocess.call('cp ~/data-science/jupyter_home/kickstart.csv.xz  /tmp/', shell=True)
time.sleep(5)
subprocess.call('xz -d /tmp/kickstart.csv.xz', shell=True)
time.sleep(5)
subprocess.call('hdfs dfs -put /tmp/kickstart.csv /', shell=True)

CONN = psycopg2.connect(
    database='tx',
    user='test_user',
    port='26257',
    host=str(sys.argv[1])
)
CONN.set_session(autocommit=True)
CUR = CONN.cursor()

CAT = subprocess.Popen(["hadoop", "fs", "-cat", "/kickstart.csv"], stdout=subprocess.PIPE)

i = 0
for line in CAT.stdout:
    i = i + 1
    l = str(line).strip('[b"\\n]').split(',')
    for k in range(0, 8):
        l[k] = l[k].strip('\'')

    if l[0] != 'category':
        sql = 'INSERT INTO tx.kickstart VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        CUR.execute(sql, l)

    if i%1000 == 0:
        print(str(i) + ' records loaded')
