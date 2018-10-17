#!/usr/bin/env python
"""Driver
This program is a driver for generating data.
"""
import sys
import pandas as pd
from sklearn.datasets import make_circles

def gen_circle(filename, sample_count):
    """Generate circle
    This function creates labeled data, one group being a circle in another.
    Input: filename, sample_size
    Output: filename.csv
    """
    features, dependent = make_circles(n_samples=sample_count, noise=0.05)
    data = pd.DataFrame(dict(x=features[:, 0], y=features[:, 1], label=dependent))
    data = data.rename(index=str, columns={'x': 'x1', 'y': 'x2', 'label': 'y'})
    data.to_csv(filename+'.csv', sep=',', encoding='utf-8', index=False)

if len(sys.argv) < 2:
    FILENAME_PASS = 'tmp'
else:
    FILENAME_PASS = str(sys.argv[1])
    
if len(sys.argv) < 3:
    SAMPLE_COUNT_PASS = 100
else:
    SAMPLE_COUNT_PASS = int(sys.argv[2])

gen_circle(FILENAME_PASS, SAMPLE_COUNT_PASS)
