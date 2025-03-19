#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pygsheets
import pandas as pd


# In[5]:


def connect_gsheet():
    #authorization
    gc = pygsheets.authorize(service_file='no_upload/dummy-376403-f836124e7806.json')
    #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
    sh = gc.open('job_monitoring')
    return sh


# In[ ]:


if __name__ == "__main__":
    # read data from database
    job_data = pd.read_csv('job_description.csv')

    # connect to google sheet
    sh = connect_gsheet()

    #select the sheet by title 
    worksheet = sh.worksheet_by_title('Sheet1')
    worksheet.clear()
    #wks_ekstra = sh.worksheet_by_title('ekstra 22')
    #wks_ekstra.clear()

    #update the first sheet with df, starting at cell B2. 
    worksheet.set_dataframe(job_data, start='A1')


# In[ ]:




