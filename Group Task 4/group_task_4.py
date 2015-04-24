"""9/9 pts"""

from __future__ import division
import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import os

main_dir = "/Users/dnoriega/Dropbox/pubpol590_sp15/data_sets/CER/tasks/4_task_data/"

####### Section 1


# CHANGE WORKING DIRECTORY (wd)
os.chdir(main_dir)
from logit_functions import *

# IMPORT DATA ------------
df = pd.read_csv(os.path.join(main_dir, 'task_4_kwh_w_dummies_wide.csv'))
df = df.dropna(axis=0, how='any')

# GET TARIFFS ------------
tariffs = [v for v in pd.unique(df['tariff']) if v != 'E']
stimuli = [v for v in pd.unique(df['stimulus']) if v != 'E']
tariffs.sort()
stimuli.sort()

# RUN LOGIT
drop = [v for v in df.columns if v.startswith("kwh_2010")]
df_pretrial = df.drop(drop, axis=1)

for i in tariffs:
    for j in stimuli:
        # dummy vars must start with "D_" and consumption vars with "kwh_"
        logit_results, df_logit = do_logit(df_pretrial, i, j, add_D=None, mc=False)

# QUICK MEANS COMPARISON WITH T-TEST BY HAND----------
# create means
grp = df_logit.groupby('tariff')
df_mean = grp.mean().transpose()
df_mean.C - df_mean.E

# do a t-test "by hand"
df_s = grp.std().transpose()
df_n = grp.count().transpose().mean()
top = df_mean['C'] - df_mean['E']
bottom = np.sqrt(df_s['C']**2/df_n['C'] + df_s['E']**2/df_n['E'])
tstats = top/bottom
sig = tstats[np.abs(tstats) > 2]
sig.name = 't-stats'

####### Section 2

#Get predicted propensity scores
df_logit['p_hat'] = logit_results.predict()

#Generate treatment indicator variable
df_logit['trt'] = 0 + (df_logit['tariff'] == 'C')

#Generate propensity score weights
df_logit['w'] = df_logit['trt']/df_logit['p_hat'] + (1 - df_logit['trt'])/(1 -df_logit['p_hat'])
df_logit['w'] = np.sqrt(df_logit['w'])

#T-test by hand
# QUICK MEANS COMPARISON WITH T-TEST BY HAND----------
# create means
grp = df_logit.groupby('tariff')
df_mean = grp.mean().transpose()
df_mean.C - df_mean.E

# do a t-test "by hand"
df_s = grp.std().transpose()
df_n = grp.count().transpose().mean()
top = df_mean['C'] - df_mean['E']
bottom = np.sqrt(df_s['C']**2/df_n['C'] + df_s['E']**2/df_n['E'])
tstats = top/bottom
sig = tstats[np.abs(tstats) > 2]
sig.name = 't-stats'

#Store results into mini-dataframe
df_logit_w = df_logit[ ['ID', 'trt', 'w'] ]


####### Section 3
# IMPORT DATA ------------
from fe_functions import *

df_long = pd.read_csv(os.path.join(main_dir, 'task_4_kwh_long.csv'))
df_long = df_long.dropna(axis=0, how='any')

#merge with mini frame
df_long = pd.merge(df_long, df_logit_w, on = ['ID'])

#Generate interaction variables
df_long['trt_trial'] = df_long.trt*df_long.trial
df_long['log_kwh'] = (df_long['kwh'] + 1).apply(np.log)

df_long['mo_str'] = np.array(["0" + str(v) if v < 10 else str(v) for v in df_long['month']])
# concatenate to make ym string values
df_long['ym'] = df_long['year'].apply(str) + "_" + df_long['mo_str']


#Set up regression variables
y = df_long['log_kwh']
P = df_long['trial']
TP = df_long['trt_trial']
w = df_long['w']
mu = pd.get_dummies(df_long['ym'], prefix = 'ym').iloc[:, 1:-1]
X = pd.concat([TP, P, mu], axis=1)

ids = df_long['ID']
y = demean(y, ids)
X = demean(X, ids)

import statsmodels.api as sm

## WITHOUT WEIGHTS
fe_model = sm.OLS(y, X) # linearly prob model
fe_results = fe_model.fit() # get the fitted values
print(fe_results.summary()) # print pretty results

# WITH WEIGHTS
## apply weights to data
y = y*w # weight each y
nms = X.columns.values # save column names
X = np.array([x*w for k, x in X.iteritems()]) # weight each X value
X = X.T # transpose (ndecessary as arrays create "row" vectors, not column)
X = DataFrame(X, columns = nms) # update to dataframe; use original names

fe_w_model = sm.OLS(y, X) # linearly prob model
fe_w_results = fe_w_model.fit() # get the fitted values
print(fe_w_results.summary()) # print pretty results
