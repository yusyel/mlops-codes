#!/usr/bin/env python
# coding: utf-8

# In[35]:


#get_ipython().system('pip freeze | grep scikit-learn')


# In[36]:


import pickle
import pandas as pd


# In[37]:


with open('model.bin', 'rb') as f_in:
    dv, lr = pickle.load(f_in)


# In[38]:


categorical = ['PUlocationID', 'DOlocationID']

def read_data(filename):
    df = pd.read_parquet(filename)
    
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    
    return df


# In[39]:


df = read_data('https://nyc-tlc.s3.amazonaws.com/trip+data/fhv_tripdata_2021-04.parquet')


# In[40]:


dicts = df[categorical].to_dict(orient='records')
X_val = dv.transform(dicts)
y_pred = lr.predict(X_val)


# In[41]:


mean = y_pred.mean()
print(mean)


# In[63]:


year=2021
month=2


# In[64]:


df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')


# In[65]:


df


# In[66]:


df['result'] = y_pred
df


# In[69]:


df_result = pd.DataFrame()


# In[70]:


df_result['ride_id'] = df['ride_id']


# In[73]:


df_result['_pred'] = y_pred


# In[75]:


#df_result.to_parquet(
    #'ourput.parquet',
    #engine='pyarrow',
    #compression=None,
    #index=False
#)


# In[ ]:




