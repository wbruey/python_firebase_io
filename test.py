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

thrust=pd.Series(thrust,index=times,name='thrust')
print(thrust)
print(thrust.shift())

start=pd.Timestamp(year=2018,month=11,day=25,hour=10,minute=30, second=0, microsecond=0) 
#print(start)

stop=pd.Timestamp(year=2018,month=11,day=25,hour=10,minute=30, second=30, microsecond=0)

#convert everything to absolute time.
thrust.index=thrust.index+start
#print(thrust)

#create time index
time_index=pd.date_range(start,stop,freq='ms')

#print(time_index)

#get coefficients
Cd=0.5 * 1.225 * 0.75 * 0.02 * 0.02
wet_weight=0.3

#convert thrust curve to absolute time
launch_data=pd.DataFrame(thrust,index=time_index)
row_count=launch_data.shape[0]
launch_data['thrust']=launch_data['thrust'].interpolate()
launch_data['alt']=np.zeros(row_count)
launch_data['vel']=np.zeros(row_count)
launch_data['accel']=np.zeros(row_count)
launch_data['drag']=np.zeros(row_count)
launch_data['mass']=np.zeros(row_count)+wet_weight
launch_data['weight']=np.zeros(row_count)+wet_weight*9.8

#do initial conditions
launch_data['alt'][0]=0
launch_data['alt'][1]=0
launch_data['vel'][0]=0
launch_data['accel'][0]=(launch_data['thrust'][0]-launch_data['drag'][0]-launch_data['weight'][0])/launch_data['mass'][0]

delta=launch_data.index[1]-launch_data.index[0]
delta=delta.total_seconds()
#print(delta)
#print(delta * 5)
#print(type(delta*5))



#print(launch_data)

#print(launch_data['first_stage_thrust'][2])






