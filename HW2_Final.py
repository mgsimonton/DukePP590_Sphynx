from __future__ import division
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
from scipy.special import stdtr

main_dir = "C:\Users\Daniel\Desktop\BigData\CER_both\electricity_revised_2012"
root = main_dir + "\Unzipped_Data"
paths = [root + "\\File" + str(v) + ".txt" for v in range(1,6)]



## --- IMPORTING DATA --- ##

# label missing values
missing = ['.', 'NA', 'NULL', '', '-', '9999999']

# import consumption data, concatenate
df = pd.concat([pd.read_table(v, sep = " ", names = ['Panid', 'Date', 'Kwh'],
    na_values  = missing)
    for v in paths], ignore_index = True)

# import assignment data, clean columns 
df_assign = pd.read_csv(root + "\\Allocations.csv", usecols = [0,1,2,3,4])
df_assign.rename(columns = {'ID' : 'Panid', 'Code' : 'Group', 'Residential - Tariff allocation': 'tariff',
    'Residential - stimulus allocation': 'stimulus'}, inplace = True)

# merge consumption and assignment data
df = pd.merge(df, df_assign)



## --- SET TREATMENT & CONTROL GROUPS --- ## 

# control group; 929 rows
df_ctr = df_assign[(df_assign.stimulus == 'E')]
df_ctr['assignment'] = 'C'

# treatment group: 281 rows
df_trt = df_assign[(df_assign.stimulus == '1') & (df_assign.tariff == 'A')]
df_trt['assignment'] = 'T'

# combine control and treatment groups
df2 = pd.concat([df_ctr, df_trt], ignore_index = True)

# merge with original data, dropping obs not in control or treatment groups
df = pd.merge(df,df2)



## --- CORRECTING DATES --- ##

# import Dan's time series correction
df_timecor = pd.read_csv(root + "\\timeseries_correction.csv", usecols = [1,7,8], parse_dates = [0])

# teasting out 5-digit date elements
df['hour_cer'] = df['Date']%100
df['day_cer'] = (df['Date']-df['hour_cer'])/100

# getting rid of 5-digit date
df = df.drop('Date',axis=1)

# merge with time series correction
df = pd.merge(df, df_timecor, on = ['hour_cer', 'day_cer'])

# break out
df['year'] = df['ts'].apply(lambda x: x.year)
df['month'] = df['ts'].apply(lambda x: x.month)
df['day'] = df['ts'].apply(lambda x: x.day)
df['ymd'] = df['ts'].apply(lambda x: x.date())


## --- DROPPING HOUR ERRORS --- ##

#Drop full row duplicates
df = df[(df.hour_cer <= 48)]



## --- SETTING TREAT-CONTROL KEYS --- ##

# testing
grp = df.groupby(['day_cer', 'Panid', 'assignment'])
agg = grp['Kwh'].sum()

# esumming by day and assignment type
agg = agg.reset_index()
grp1 = agg.groupby(['day_cer', 'assignment'])

# setting keys
trt = {k[0]: agg.Kwh[v].values for k, v in grp1.groups.iteritems() if k[1] == 'T'} # get set of all treatments by date
ctrl = {k[0]: agg.Kwh[v].values for k, v in grp1.groups.iteritems() if k[1] == 'C'} # get set of all controls by date
keys = ctrl.keys()



## --- P-VALUES AND T-VALUES --- ##

tstats = DataFrame([(k, np.abs(ttest_ind(trt[k], ctrl[k], equal_var=False)[0])) for k in keys],
    columns = ['day_cer', 'tstat'])
pvals = DataFrame([(k, np.abs(ttest_ind(trt[k], ctrl[k], equal_var=False)[1])) for k in keys],
    columns = ['day_cer', 'pval'])

# Combine the two statistics into one dataframe    
t_p = pd.merge(tstats, pvals)
   
# SortING
t_p.sort(['day_cer'], inplace=True)
t_p.reset_index(inplace=True, drop=True)
   
      
            
## --- DAILY PLOT --- ##   

# initialize plot
fig1 = plt.figure()

# t-stat plot
ax1 = fig1.add_subplot(2,1,1)
ax1.plot(t_p['tstat'])
ax1.axhline(2, color='r', linestyle='--')
ax1.set_title('Daily t-stats')

# p-value plot
ax2 = fig1.add_subplot(2,1,2)
ax2.plot(t_p['pval'])
ax2.axhline(0.05, color='r', linestyle='--')
ax2.set_title('Daily p-values')




# Hey Dan, we worked hard to knock this out today; however, our computers' ram struggled to produce the charts at the end; therefore, we've only gotten to one.


