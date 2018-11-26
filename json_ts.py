import json
import argparse
import csv
import logging
import pandas as pd
import numpy as np
from scipy import integrate
import time


class json_time_series:

    def __init__(self,df):  #df is a pandas dataframe
        
        #get column headers from data frame.
        col_index=0
        columns={}
        for column in df:
            column_info={"name":column}
            columns[str(col_index)]=column_info
            col_index=col_index+1
        
        #create skeleton of time series
        self.data={"docType":"jts",
                   "version":"1.0",
                   "header": {
                        "startTime":str(df.index[0]),
                        "endTime":str(df.index[-1]),
                        "recordCount":df.shape[0],
                        "columns":columns,
                    },
                    "data":[]
                    }
        
        # add the data to the time series object
        for row in range(df.shape[0]):
            #first create the "f" value object
            col_index=0
            f_object={}
            for column in df:
                f_object[str(col_index)]={"v":df[column][row]}
                col_index=col_index+1
                
            time_stamped_object={"ts":str(df.index[row]),"f":f_object}
            self.data['data'].append(time_stamped_object)
            
    def save_jts(self,outfile):
        with open('data.json', 'w') as outfile:
            json.dump(self.data, outfile)                    