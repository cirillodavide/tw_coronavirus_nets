from datetime import datetime

import pathlib
import pandas as pd


# Save dataframe to csv
def save_csv(dataframe, file_name):
    today = datetime.strftime(datetime.now(), '%m%d%y')
    f_name = pathlib.Path(__file__).parents[2].joinpath('sna', 'graphs', file_name+'_'+today+'.csv')
    dataframe.to_csv(f_name,index=False)
    return(f_name)