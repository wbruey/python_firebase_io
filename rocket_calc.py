import argparse
import json
import csv
import logging
import pandas as pd
import numpy as np
from scipy import integrate

def simple_integrate(time_series):
	return integrate.trapz(time_series.values, time_series.index.astype('timedelta64[ms]') / 1000.0)

def setup_my_logger():
    logging.basicConfig(filename='rocket.log',level=logging.DEBUG,format='%(asctime)s %(message)s')
    
def log_to_console():
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)    

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
            self.thrust=pd.Series(thrust,index=times,name='thrust')
            self.burn_duration=self.thrust.index[-1]-self.thrust.index[0]
			
            #create mass time series with the assumption that it will be the same curve shape as thrust file
            self.specific_impulse=simple_integrate(self.thrust)  #integrate thrust curve to be used in normaization
            mass_loss=self.thrust/self.specific_impulse*self.prop_mass #normalize thrust curve and multiple by mass loss
            mass_loss.name='mass_loss'  #name the mass_loss timeseries.  This is the instantanious per/second mass loss at any given time
            tempdf=pd.DataFrame(mass_loss,columns=['mass_loss'])  #create a temp data frame to find cumulitve mass loss at any given time
            tempdf['time']=mass_loss.index  #with time so we can do math on it.  Time is a column now so we can convert it to a float to do math to find cumulitve mass loss at any given time
            tempdf['dtime']=(tempdf['time']-tempdf['time'].shift()).fillna(0).astype('timedelta64[ms]')/1000.0  #another column in the temp data frame is delta time of each timestamp since that's not uniform for a thrust curve
            self.mass=self.initial_mass-(((tempdf['mass_loss']+tempdf['mass_loss'].shift(-1).fillna(0))/2.0)*tempdf['dtime']).cumsum() #ad up the lsot mass trapazoid stype and subtract it from inital mass
            self.mass.name='mass'  #name the time series
                        
            #put mass and thrust into a milisecond dataframe
            time_index=pd.timedelta_range(start=pd.Timedelta(value=0,unit='ms') ,end=self.thrust.index[-1],freq='ms') #create a time index of milisecond increments for as long as the thrust (and mass) time series are
            self.engine_data=pd.DataFrame(self.thrust,index=time_index) #create an engine_data frame with thrust and the time index
            self.engine_data['mass']=self.mass #add mass to the data_frame
            self.engine_data=self.engine_data.interpolate() #intermpolate to give us a value for mass and thrust at any given time
            
			
			
			
            logging.info('loaded engine ' + part_num + ' prop mass '+str(self.prop_mass)+' final_mass '+str(self.final_mass)+' initial_mass '+str(self.initial_mass))
        except Exception:
            logging.exception('Failed to Load Engine')

class stage:

    def __init__(self,dry_mass,engines,cross_section,drag_coeff):  #engines is a list of engines  - dry mass is mass of stage with NO engines installed
        #define the static parametres
        self.dry_mass=dry_mass
        self.engines=engines
        self.cross_section=cross_section
        self.drag_coeff=drag_coeff
        self.wet_mass=self.dry_mass
        self.prop_mass=0
        self.burn_duration=pd.Timedelta(0,'ms')
        logging.info('stage added with ' + str(self.dry_mass) + ' kg of dry mass and the following engines')
        
        #for each engine add the masses to the stage
        for engine in self.engines:
            self.burn_duration=max(self.burn_duration,engine.burn_duration)
            logging.info(engine.part_num)
            self.wet_mass=self.wet_mass+engine.initial_mass
            self.prop_mass=self.prop_mass+engine.prop_mass
        self.final_mass=self.wet_mass-self.prop_mass
        
        #create a data frame "stage_data" with thrust and mass at all times
        time_index=pd.timedelta_range(start=pd.Timedelta(value=0,unit='ms'), end=self.burn_duration,freq='ms')
        self.stage_data=pd.DataFrame(index=time_index)
        self.stage_data['thrust']=np.zeros(len(time_index))
        self.stage_data['mass']=np.zeros(len(time_index))+self.dry_mass
        for engine in self.engines:
            tempDF=pd.DataFrame(engine.engine_data,index=time_index)
            tempDF['thrust']=tempDF['thrust'].fillna(0)  #if thrust is undefined after the engine data ends, fill it with zeros.
            tempDF['mass']=tempDF['mass'].interpolate()  #if mass is undefined after the engine data ends, fill it with last value
            self.stage_data=self.stage_data+tempDF  # add the temp to the stage data
        
            
        
        logging.info('this stage has a '+str(self.cross_section) + ' m^2 cross section and a drag coefficient of ' + str(self.drag_coeff) +' and a total wet mass of ' + str(self.wet_mass) + ' after the engines have burned, this stage will have a final mass of ' + str(self.final_mass))
       
class vehicle:

    def __init__(self,stages):  #stages is a LIST of stage objects
        self.stages=stages
        logging.info('vehicle has '+str(len(self.stages)) + ' stages ')
        self.wet_mass=0
        self.burn_duration=pd.Timedelta(0,'ms')
        
        
        #for each stage, add the mass of all higher stages, add a stage_number to the stage_data frame
        mass_above=0
        self.stage_count=len(stages)
        stage_index=self.stage_count
        for stage in reversed(self.stages):
            self.wet_mass=self.wet_mass+stage.wet_mass
            stage.stage_data['mass']=stage.stage_data['mass']+mass_above
            mass_above=mass_above+stage.wet_mass   
            self.burn_duration=self.burn_duration+stage.burn_duration
            stage.stage_data['stage_number']=np.zeros(len(stage.stage_data))+stage_index
            stage_index=stage_index-1
        
        #for each stage concatenate them into a vehicle_data frame
        self.vehicle_data=pd.DataFrame()
        stage_sep=pd.Timedelta(0,'ms')
        for stage in self.stages:
            #add offsets for each stage when they begin their time stamp
            stage.stage_data.index=stage.stage_data.index+stage_sep
            stage_sep=stage.stage_data.index[-1]
            self.vehicle_data=pd.concat([self.vehicle_data,stage.stage_data])
  
        logging.info('vehicle has wet mass of ' + str(self.wet_mass) + ' kg ')

        
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


