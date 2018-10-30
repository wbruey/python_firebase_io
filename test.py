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

thrust=pd.Series(thrust,index=times,name='first_stage_thrust')
#print(thrust)

start=pd.Timestamp(year=2018,month=11,day=25,hour=10,minute=30, second=0, microsecond=0) 
#print(start)

stop=pd.Timestamp(year=2018,month=11,day=25,hour=10,minute=30, second=30, microsecond=0)

#convert everything to absolute time.
thrust.index=thrust.index+start
#print(thrust)

#create time index
time_index=pd.date_range(start,stop,freq='ms')
#print(time_index)

#convert thrust curve to absolute time
launch_data=pd.DataFrame(thrust,index=time_index)
launch_data['first_stage_thrust']=launch_data['first_stage_thrust'].interpolate()

print(launch_data)

print(launch_data['first_stage_thrust'][2])


