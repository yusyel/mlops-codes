# %%
import datetime
from datetime import time
from datetime import datetime, timedelta
from time import strptime

# %%


def get_paths(Date=None):

    if Date == None:
        Date = datetime.today()
        train_path = "./data/fhv_tripdata_2022-04.parquet"
        val_path = "./data/fhv_tripdata_2022-05.parquet"
        print("None, Today!")
    else:
        train_path = "./data/fhv_tripdata_2022-06.parquet"
        val_path = "./data/fhv_tripdata_2022-07.parquet"
        print("Not none!")







# %%
#  c. If a date value is supplied, get 2 months before the date as the training data, and the previous month as validation data