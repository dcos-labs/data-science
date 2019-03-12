#!/usr/bin/env python
"""Driver
This program is a driver for generating data.
"""
import warnings
warnings.simplefilter("ignore")
import sys
import numpy as np
import pandas as pd
from sklearn.datasets import make_circles

def gen_circle(filename, sample_count):
    """Generate circle
    This function creates labeled data, one group being a circle in another.
    It then takes apart one of the features into multiple features.
    Input: filename, sample_size
    Output: filename.csv [x1, x2, x3, x4, x5, y]
    """
    features, dependent = make_circles(n_samples=sample_count, noise=0.05)
    tmp = pd.DataFrame(dict(x=features[:, 0], y=features[:, 1], label=dependent))
    x0 = np.round(tmp['x'], 8)
    x1 = np.round(np.random.normal(0, 1, sample_count), 8)
    x2 = np.round(np.random.normal(0, 1, sample_count), 8)
    x3 = np.round(np.random.normal(0, 1, sample_count), 8)
    x4 = np.round(x0 - (x1 + x2 + x3), 8)
    x5 = np.round(tmp['y'], 8)
    y = tmp['label']
    data = pd.DataFrame({'x1':x1, 'x2':x2, 'x3':x3, 'x4':x4, 'x5':x5, 'y':y})
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
