import argparse
import json
import csv
import logging
import pandas as pd
import numpy as np
from scipy import integrate

def simple_integrate(time_series):
	return integrate.trapz(time_series.values, time_series.index.astype(np.int64) / 10**9)

def setup_my_logger():
    logging.basicConfig(filename='rocket.log',level=logging.DEBUG,format='%(asctime)s %(message)s')
    
def log_to_console():
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)    

class vehicle:

    def __init__(self,stages):  #stages is a LIST of stage objects
        self.stages=stages
        logging.info('vehicle has '+str(len(self.stages)) + ' stages ')
        self.wet_mass=0
        for stage in self.stages:
            self.wet_mass=self.wet_mass+stage.wet_mass
        logging.info('vehicle has wet mass of ' + str(self.wet_mass) + ' kg ')

class stage:

    def __init__(self,dry_mass,engines,cross_section,drag_coeff):  #engines is a list of engines
        self.dry_mass=dry_mass
        self.engines=engines
        self.cross_section=cross_section
        self.drag_coeff=drag_coeff
        self.wet_mass=self.dry_mass
        self.prop_mass=0
        logging.info('stage added with ' + str(self.dry_mass) + ' kg of dry mass and the following engines')
        for engine in self.engines:
            logging.info(engine.part_num)
            self.wet_mass=self.wet_mass+engine.initial_mass
            self.prop_mass=self.prop_mass+engine.prop_mass
        self.final_mass=self.wet_mass-self.prop_mass
        logging.info('this stage has a '+str(self.cross_section) + ' m^2 cross section and a drag coefficient of ' + str(self.drag_coeff) +' and a total wet mass of ' + str(self.wet_mass) + ' after the engines have burned, this stage will have a final mass of ' + str(self.final_mass))
       

class launch:

    def __init__(self,vehicle,sim_duration,density): #density is in kg/m^3  #duration in seconds

        #Define physics initial conditions
        self.density=density
        self.initial_conditions={}
        self.initial_conditions['alt0']=0
        self.initial_conditions['alt1']=0
        self.initial_conditions['vel0']=1
        m0=vehicle.wet_mass
        cross_section_0=0.0
        drag_coeff_0=0.0
        #gather initial conditions from all stages and engines
        for stage in vehicle.stages:
            cross_section_0=max(cross_section_0,stage.cross_section)
            drag_coeff_0=max(drag_coeff_0,stage.drag_coeff)
        self.initial_conditions['mass0']=m0
        self.initial_conditions['Cd0']=0.5*density*drag_coeff_0*cross_section_0
        self.initial_conditions['weight0']=m0*9.8

        logging.info('launch initial conditions are ....')
        logging.info(self.initial_conditions)

        #build empty dataframe skelton to populate with calculations
        self.sim_duration=pd.Timedelta(seconds=sim_duration)
        t_start=pd.Timestamp(year=2018,month=11,day=25,hour=10,minute=30, second=0, microsecond=0)
        t_stop=t_start+self.sim_duration
        logging.info('building simulation data structure of a ' + str(self.sim_duration.total_seconds())+'seconds')
        #time axis
        time_index=pd.date_range(t_start,t_stop,freq='ms')
        self.launch_data=pd.DataFrame(index=time_index)
        row_count=self.launch_data.shape[0] #row count is equivalent to number of time incriments (miliseconds) in sim
        #add blank columns to define data structure size
        self.launch_data['stage_burn']=np.zeros(row_count)
        self.launch_data['thrust']=np.zeros(row_count)
        self.launch_data['mass']=np.zeros(row_count)
        self.launch_data['weight']=np.zeros(row_count)
        self.launch_data['drag']=np.zeros(row_count)
        self.launch_data['accel']=np.zeros(row_count)
        self.launch_data['vel']=np.zeros(row_count)
        self.launch_data['alt']=np.zeros(row_count)        
        logging.info('blank simulation data structure assembled adding')





class engine:

    def __init__(self,part_num='F15',delay='0'): # expects there to be an xxx.thrust and an xxx.json to import.  You can get thurst curves here: http://www.thrustcurve.org/simfilesearch.jsp?id=2021
        try:
            #open the thrust attributes file and load the static attributes for engine
            self.part_num=part_num
            with open(self.part_num+'.attributes') as json_file:
                    self.attributes=json.load(json_file)
            self.prop_mass=self.attributes['prop_mass']
            self.final_mass=self.attributes['final_mass']
            self.initial_mass=self.attributes[delay]['initial_mass']
            self.delay=self.attributes[delay]['delay']
            self.isp=self.attributes['total_impulse']
            self.thrust_uncertainty_percent=self.attributes['impulse_std_dev_percent']

            #load thrust file and create a time series from it.
            with open(self.part_num+'.thrust', 'rb') as csvfile:
                thrust_reader=csv.reader(csvfile,delimiter= ' ')
                times=[]
                thrust=[]
                for row in thrust_reader:
                    times.append(pd.Timedelta(row[0] +' seconds'))
                    thrust.append(float(row[1]))
            self.thrust=pd.Series(thrust,index=times)
            self.burn_duration=self.thrust.index[-1]-self.thrust.index[0]
			
            #create mass curve from thrust file
            self.specific_impulse=simple_integrate(self.thrust)
            self.mass_loss=self.thrust/self.specific_impulse*self.prop_mass
            self.mass=self.initial_mass-self.mass_loss.cumsum()
            
			
			
			
            logging.info('loaded engine ' + part_num + ' prop mass '+str(self.prop_mass)+' final_mass '+str(self.final_mass)+' initial_mass '+str(self.initial_mass))
        except Exception:
            logging.exception('Failed to Load Engine')


        


