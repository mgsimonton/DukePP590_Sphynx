from __future__ import division
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import os

# PATHING AND IMPORTING --------------

main_dir = "C:\Users\samjh_000"
csv_file = "\Desktop\CES raw\SME and Residential allocations.csv"
root = main_dir + "\Desktop\CES raw"
paths = [root + "\File" + str(v) + ".txt" for v in range(1,7)]

missing = ['.', 'NA', 'NULL', '', '-', '9999999']

#Imports all dataframes as one giant list

df_big = pd.concat([pd.read_table(v, sep = " ", names = ['ID', 'DayTime', 'consump'], na_values = missing) for v in paths], ignore_index = True)

# DROP DUPLICATES --------------

#Drop full row duplicates
df_big = df_big.drop_duplicates()
df_big = df_big.drop_duplicates(take_last = True)

# DROP DST ERRORS --------------

df_big['Hour'] = df_big['DayTime']%100 
# creates new column returning last 2 digits of DayTime (i.e., just the half hour indicator)
df_big = df_big[(df_big.Hour <= 49)]
# creates a new dataframe that omits the impossible half hour indicators 49 and 50
test = df_big[(df_big.Hour >= 49)]
test
# 'test' list is empty, confirming that the 49 and 50 values are dropped from new DataFrame


# DROP NAs --------------

#Drop NAs (including former 999999 entries
df_big.dropna()


# MERGING DATASETS --------------

#import Excel data
df_excel = pd.read_table(main_dir + csv_file, usecols = ['ID', 'Code', 'Residential - Tariff allocation', 'Residential - stimulus allocation', 'SME allocation'])

#Merge Excel data based on meter IDs in common between sets
pd.merge(df_clean, df_excel) 
#Leaving NaNs in for now