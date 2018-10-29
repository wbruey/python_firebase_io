import csv
import json
import numpy as np
import pandas as pd


def times_two(x):
    return x*2

with open('F15.attributes') as json_file:
    F15_attributes=json.load(json_file)

with open('F15.thrust', 'rb') as csvfile:
    thrust_reader=csv.reader(csvfile,delimiter=' ')
    times=[]
    thrust=[]
    for row in thrust_reader:
        times.append(pd.Timedelta(row[0]+' seconds'))
        thrust.append(float(row[1]))

ts=pd.Series(thrust,index=times)
print(ts)
        

y=2*ts

print(y)





