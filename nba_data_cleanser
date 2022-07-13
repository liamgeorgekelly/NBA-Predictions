## NBA Data Cleanser
# This program cleans data by filling in missing values.

import numpy as np
from numpy import pi, log, sin, cos, dot, e
import pandas as pd
from datetime import date
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from alive_progress import alive_bar
from sklearn.linear_model import LogisticRegression
from sklearn import model_selection
from sklearn import preprocessing
from sklearn import metrics

# MySQL Credentials
hostname = "localhost"
uname = "root"
pwd = "rootroot"
dbname = "nba_statistics" # Schema name
tablename_s = 'nba_db' # Source table name
tablename_d = 'nba_db_c' # Destination table name

# Import nba_seasons_db data from the database:
engine = create_engine("mysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=dbname, user=uname, pw=pwd))
df = pd.read_sql(sql = tablename_s, con = engine).set_index('index')

# Fill Missing Values
# Fill WS Values
print(df['WS'].isnull().values.any())
nan_index = df.index[df['WS'].isnull()]
df.loc[nan_index,'WS'] = df.WS.mean()
print(df['WS'].isnull().values.any())

# Fill TRB Values
print(df['TRB'].isnull().values.any())
nan_index = df.index[df['TRB'].isnull()]
df.loc[nan_index,'TRB'] = df.TRB.mean()
print(df['TRB'].isnull().values.any())

# Fill STL Values
print(df['STL'].isnull().values.any())
nan_index = df.index[df['STL'].isnull()]
df.loc[nan_index,'STL'] = df.STL.mean()
print(df['STL'].isnull().values.any())

# Fill BLK Values
print(df['BLK'].isnull().values.any())
nan_index = df.index[df['BLK'].isnull()]
df.loc[nan_index,'BLK'] = df.BLK.mean()
print(df['BLK'].isnull().values.any())

df.to_sql(con = engine, name=tablename_d, if_exists='replace')
