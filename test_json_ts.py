import json_ts as jts
import pandas as pd
import numpy as np

df = pd.DataFrame(np.random.randint(0,100,size=(6, 4)), columns=list('ABCD'))

print(df)

first_series=jts.json_time_series(df)

print(first_series.data)