#!/usr/bin/env python
"""Driver
This loads data into Cockroach DB.
Script expects Cockroach IP is passed.
"""
import psycopg2
import re
import subprocess
import sys
import time

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

conn = psycopg2.connect(
    database='tx',
    user='test_user',
    port='26257',
    host=str(sys.argv[1])
)
conn.set_session(autocommit=True)
cur = conn.cursor()

cat = subprocess.Popen(["hadoop", "fs", "-cat", "/kickstart.csv"], stdout=subprocess.PIPE)

i = 0
for line in cat.stdout:
    i = i + 1
    l = str(line).strip('[b"\\n]').split(',')
    for k in range(0,8):
        l[k] = l[k].strip('\'')

    if l[0] != 'category':
        sql = 'INSERT INTO tx.kickstart VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cur.execute(sql, l)

    if i%1000 == 0:
        print(str(i) + ' records loaded')
