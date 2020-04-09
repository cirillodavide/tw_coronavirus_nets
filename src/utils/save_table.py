from datetime import datetime

import pathlib
import pandas as pd


# Save dataframe to csv
def save_csv(dataframe, file_name, database, collection):
    today = datetime.strftime(datetime.now(), '%d%m%y')
    f_name = pathlib.Path(__file__).parents[2].joinpath('sna', 'graphs', database+'.'+collection+'.'+file_name+'.'+today+'.tsv')
    dataframe.to_csv(f_name,index=False,sep='\t', encoding = 'utf-8')
    return(f_name)