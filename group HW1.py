from __future__ import division
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import os

#Pathing
main_dir = "C:\Users\samjh_000"
csv_file = "\Desktop\CES raw\SME and Residential allocations.csv"
root = main_dir + "\Desktop\CES raw"

paths = [root + "\File" + str(v) + ".txt" for v in range(1,7)]

missing = ['.', 'NA', 'NULL', '', '-', '9999999']

#Imports all dataframes as one giant list
###TASK: add concatenate function into this line to save on load times 
#list_of_dfs = [pd.read_table(v, sep = " ", names = ['ID', 'DayTime', 'consump'], na_values = missing) for v in paths]
df_big = pd.concat([pd.read_table(v, sep = " ", names = ['ID', 'DayTime', 'consump'], na_values = missing) for v in paths], ignore_index = True)


#df_big = pd.concat([df1, df2, df3], ignore_index = True)

#Drop full row duplicates
df_big = df_big.drop_duplicates()
df_big = df_big.drop_duplicates(take_last = True)

#List of affected days
#df_big[df_big.DayTime == 45202]
#df_big[df_big.DayTime == 45203]
#df_big[df_big.DayTime == 66949]   
#df_big[df_big.DayTime == 66950]   
#df_big[df_big.DayTime == 29849]   
#df_big[df_big.DayTime == 29850]   

#drop all records for DST days

#example for filtering out days/times
#a = 345999%100
#day = ([] - a)/100

#Drop NAs (including former 999999 entries
df_big.dropna()


#import Excel data
df_excel = pd.read_table(main_dir + csv_file, usecols = ['ID', 'Code', 'Residential - Tariff allocation', 'Residential - stimulus allocation', 'SME allocation'])

#Merge Excel data based on meter IDs in common between sets
pd.merge(df_clean, df_excel) 
#Leaving NaNs in for now