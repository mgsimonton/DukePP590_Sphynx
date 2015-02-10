from __future__ import division
from pandas import Series, DataFrame
import pandas as pd
import numpy as np

#Pathing
main_dir = "C:\Users\samjh_000"
csv_file = "\Desktop\CES raw\SME and Residential allocations.csv"
txt_file1 = "\Desktop\CES raw\File1.txt"
txt_file2 = "\Desktop\CES raw\File2.txt"
txt_file3 = "\Desktop\CES raw\File3.txt"
txt_file4 = "\Desktop\CES raw\File4.txt"
txt_file5 = "\Desktop\CES raw\File5.txt"
txt_file6 = "\Desktop\CES raw\File6.txt"

#999999 values will be replaced with NaN upon import
missing = ['.', 'NA', 'NULL', '', '-', '9999999']
header = ['ID', 'DayTime', 'consump']

#Import data frames
df1 = pd.read_table(main_dir + txt_file1, sep = "\s", na_values = missing)
df2 = pd.read_table(main_dir + txt_file2, sep = "\s", na_values = missing)
df3 = pd.read_table(main_dir + txt_file3, sep = "\s", na_values = missing)
df4 = pd.read_table(main_dir + txt_file4, sep = "\s", na_values = missing)
df5 = pd.read_table(main_dir + txt_file5, sep = "\s", na_values = missing)
df6 = pd.read_table(main_dir + txt_file6, sep = "\s", na_values = missing)

#Put headers on each df before stacking!
df1.columns = header
df2.columns = header
df3.columns = header
df4.columns = header
df5.columns = header
df6.columns = header

#Stacks on stacks on stacks
df_big = pd.concat([df1, df2, df3], ignore_index = True)

#Drop full duplicates, going from top and bottom (might crash computer!)
df_big = df_big.drop_duplicates()
df_big = df_big.drop_duplicates(take_last = True)

#Look for screwed up days
df_big[df_big.DayTime == 45202]
df_big[df_big.DayTime == 45203]
df_big[df_big.DayTime == 66949]  
df_big[df_big.DayTime == 66950]  
df_big[df_big.DayTime == 29849]   
df_big[df_big.DayTime == 29850]   

#drop all records for DST days
#df_new = df1[df1.DayTime > 66900]
#df1.DayTime < 67000]

#######
#Failing


#df1.drop(df1['DayTime'] == 452**)
#19943%100: last two
#19943 - a (mod)/100

#########


#Drop NAs (including former 999999 entries
df1.dropna()

#remove entries w/999999 for consumption

#import Excel data
df_excel = pd.read_csv(main_dir + csv_file, usecols = ['ID', 'Code', 'Residential - Tariff allocation', 'Residential - stimulus allocation', 'SME allocation'])

#Merge Excel data based on meter IDs in common between sets
df_merged = pd.merge(df1, df_excel) 
## What to do about meter IDs w/no Excel labels (NaNs)?


