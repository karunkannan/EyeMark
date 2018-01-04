'''
Author: Karun Kannan
Last Update: 1/3/18
'''

import numpy as np
import pickle
import csv

error = []
with open('test/thickness.pkle', 'rb') as f:
    thickness = pickle.load(f)

with open('test/control.csv') as csv_file:
    reader = csv.reader(csv_file)
    reader.__next__()
    for row in reader:
        pred = thickness[row[0]][15]
        control = np.float32(row[1])
        loss = np.absolute((pred - control)/control)
        print("%s error: %.2f" % (row[0], loss))
        error.append(loss)
    print("Average Error: %.2f" % np.mean(error))
