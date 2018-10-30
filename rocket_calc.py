import argparse
import json
import csv
import logging

class vehicle:

    def __init__(self,stages,cross_section,drag_coeff):  #stages is a LIST of stage objects
        self.stages=stages
        self.cross_section=cross_section
        self.drag_coeff=drag_coeff


class stage:

    def __init__(self,dry_mass,engine):
        self.dry_mass=dry_mass
        self.engine=engine

class launch:

    def __init__(self,T0,density):
        self.T0=T0
        self.density=density




class engine:

    def __init__(self,part_num='F15',delay='0'): # expects there to be an xxx.thrust and an xxx.json to import.  You can get thurst curves here: http://www.thrustcurve.org/simfilesearch.jsp?id=2021
        self.part_num=part_num
        self.delay=delay
        with open(self.engine_PN+'.attributes') as json_file:
            self.attributes=json.load(json_file)

        with open(self.engine_PN+'.thrust', 'rb') as csvfile:
            thrust_reader=csv.reader(csvfile,delimiter= ' ')
            times=[]
            thrust=[]
            for row in thrust_reader:
                times.append(pd.Timedelta(row[0] +' seconds'))
                thrust.append(float(row[1]))

        self.thrust=pd.Series(thrust,index=times)


