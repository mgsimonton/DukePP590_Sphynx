from __future__ import division
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import os
from scipy.stats import ttest_ind
from scipy.special import stdtr

main_dir = "C:\Users\samjh_000\Desktop"
root = main_dir + "\CES raw"

# PATHING --------------
paths = [os.path.join(root,v) for v in os.listdir(root) if v.startswith("File")]

# IMPORT AND STACK ---------
df = pd.concat([pd.read_table(v, names = ['panid', 'date', 'kwh'], sep = " ", header=None, nrows = 2000000) for v in paths],
    ignore_index = True)
    
#Import spreadsheet w/treatment assignments    
df_assign = pd.read_csv(root + "\SME and Residential Allocations.csv", usecols = [0,1,2,3,4])
df_assign.rename(columns = {'Residential - Tariff allocation': 'tariff', 'Residential - stimulus allocation': 'stimulus'}, inplace = True)

#Merge w/consumption data
df = pd.merge(df, df_assign)


#Set treatment and control groups in df
# Control group = observations where 'Residential stimulus' = E
#Treatment group = observations where 'Residential stimulus' = 1
# -OR- where 'Residential tarrif' = A
df_ctrl = df_assign[df_assign.stimulus == 'E']
df_ctrl['assignment'] = 'C'

df_trt1 = df_assign[df_assign.stimulus == '1']  
df_trt1['assignment'] = 'T' 

df_trt2 = df_assign[df_assign.stimulus == 'A']  
df_trt2['assignment'] = 'T' 

#Combine two treatment groups into one
df_trt = pd.concat([df_trt1, df_trt2], ignore_index = True)

#Combine all processed observations
df2 = pd.concat([df_trt, df_ctrl], ignore_index = True)

#Remerge w/original consumption data
df = pd.merge(df,df2)

# MERGE ---------

df_timecor = pd.read_csv(root + "/timeseries_correction.csv", usecols = [2,3,4,5,6,9,10], parse_dates = [0])

# AGGREGATION (DAILY) ---------------
#Generate day and hour assignments
df['hour_cer'] = df['date']%100
df['day_cer'] = (df['date'] - df['hour_cer'])/100

df = df.drop('date',axis=1)
df = pd.merge(df, df_timecor, on = ['hour_cer', 'day_cer'])

#Group

grp = df.groupby(['panid','date', 'assignment'])
agg = grp['kwh'].sum()

# reset the index (multilevel at the moment)
agg = agg.reset_index() # drop the multi-index
grp = agg.groupby(['date', 'assignment'])

#Split into treatment and controls
trt = {k[0]: agg.kwh[v].values for k, v in grp.groups.iteritems() if k[1] == 'T'} # get set of all treatments by date
ctrl = {k[0]: agg.kwh[v].values for k, v in grp.groups.iteritems() if k[1] == 'C'} # get set of all controls by date
keys = ctrl.keys()

#t-test
tstats = DataFrame([(k, np.abs(ttest_ind(trt[k], ctrl[k], equal_var=False)[0])) for k in keys],
    columns = ['day', 'tstat'])
#p-value
pvals = DataFrame([(k, np.abs(ttest_ind(trt[k], ctrl[k], equal_var=False)[1])) for k in keys],
    columns = ['day', 'pval'])    

#Combine the two statistics into one dataframe    
t_p = pd.merge(tstats, pvals)
   
#Sort
t_p.sort(['day'], inplace=True)
t_p.reset_index(inplace=True, drop=True)
      
#Daily Plot --------------     
fig1 = plt.figure() # initialize plot

ax1 = fig1.add_subplot(2,1,1)
ax1.plot(t_p['day'], t_p['tstat'])
ax1.axhline(2, color='r', linestyle='--')
ax1.set_title('Daily t-stats')

ax2 = fig1.add_subplot(2,1,2)
ax2.plot(t_p['pval'])
ax2.axhline(0.05, color='r', linestyle='--')
ax2.set_title('Daily p-values')


