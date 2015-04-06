## group task 3 
### df = allocation_subsamp.csv
### df1 = subsample from "allocation_subsamp"
### df2 = kwh_redux_pretrial.csv
### df3 = merge df1 + df2
### df4 = merge df + agg_piv (ready for logit)

from __future__ import division
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import statsmodels.api as sm

main_dir = "/Users/shiyaowu/Desktop/PUBPOL590/"
root = main_dir + "data/3_task_data/"

df = pd.read_csv(root + "allocation_subsamp.csv")

# 1. create 5 unique vectors using the data from allocation_subsamp.csv 
Ctrl = df["ID"][df.tariff == "E"]
A1 = df["ID"][(df.tariff == "A")&(df.stimulus == "1")]
A3 = df["ID"][(df.tariff == "A")&(df.stimulus == "3")]
B1 = df["ID"][(df.tariff == "B")&(df.stimulus == "1")]
B3 = df["ID"][(df.tariff == "B")&(df.stimulus == "3")]


# 2. set the random seed to 1789
np.random.seed(1789)


# 3. use the function np.random.choice and extract the following sample size 
#    without replacement: (THE ORDER MATTERS)
ctrl = np.random.choice(Ctrl, size=300, replace=False)
a1 = np.random.choice(A1, size=150, replace=False)
a3 = np.random.choice(A3, size=150, replace=False)
b1 = np.random.choice(B1, size=50, replace=False)
b3 = np.random.choice(B3, size=50, replace=False)


# 4. create a DataFrame with all the sampled IDs.
cols = ['ID']
ctrl = pd.DataFrame(data = ctrl,columns = cols)
a1 = pd.DataFrame(data = a1,columns = cols)
a3 = pd.DataFrame(data = a3,columns = cols)
b1 = pd.DataFrame(data = b1,columns = cols)
b3 = pd.DataFrame(data = b3,columns = cols)
df1 = pd.concat([ctrl,a1,a3,b1,b3])
df1.reset_index(inplace = True,drop = True)


# 5. import the consumption data from kwh_redux_pretrial.csv
df2 = pd.read_csv(root + "kwh_redux_pretrial.csv")


# 6. merge the consumption data with the sampled IDs, which will strip away a 
#    large portion of the original consumption dataframe.
df3 = pd.merge(df1,df2,on = 'ID')


# 7. compute aggregate monthly consumption for each panel ID.
grp = df3.groupby(['year','month','ID'])
agg = grp['kwh'].sum().reset_index()


# 8. pivot the data from long to wide, so that variable kwh_[month] exists for 
#    each different [month].
agg['mon_str'] = ['0' + str(v) if v < 10 else str(v) for v in agg['month']] 
agg['kwh_ym'] = 'kwh' + '_' + agg.year.apply(str) + '_' + agg['mon_str']
agg_piv = agg.pivot('ID','kwh_ym','kwh')
agg_piv.reset_index(inplace = True)
agg_piv.columns.name = None


# 9. merge the wide dataset with the allocation data from allocation_subsamp.csv.
df4 = pd.merge(df,agg_piv,on = 'ID')


# 10. compute a logit model comparing each treatment group to the control (4 logit 
#    models total) using only the consumption data as independent variables.

c = df4['tariff'] == 'E'
ctrl = df4[c]
ctrl.code = 0

## block by treatment
trt_a1 = df4[(df4.tariff == "A")&(df4.stimulus == "1")]
trt_a3 = df4[(df4.tariff == "A")&(df4.stimulus == "3")]
trt_b1 = df4[(df4.tariff == "B")&(df4.stimulus == "1")]
trt_b3 = df4[(df4.tariff == "B")&(df4.stimulus == "3")]

## create dataframe for each comparison
ctrl_a1 = pd.concat([ctrl,trt_a1])
ctrl_a3 = pd.concat([ctrl,trt_a3])
ctrl_b1 = pd.concat([ctrl,trt_b1])
ctrl_b3 = pd.concat([ctrl,trt_b3])

## independent variables
kwh_cols_a1 = [v for v in ctrl_a1.columns.values if v.startswith ('kwh')]
kwh_cols_a3 = [v for v in ctrl_a3.columns.values if v.startswith ('kwh')]
kwh_cols_b1 = [v for v in ctrl_b1.columns.values if v.startswith ('kwh')]
kwh_cols_b3 = [v for v in ctrl_b3.columns.values if v.startswith ('kwh')]

## define variables
y_a1 = ctrl_a1['code']
x_a1 = ctrl_a1[kwh_cols_a1]
x_a1 = sm.add_constant(x_a1)

y_a3 = ctrl_a3['code']
x_a3 = ctrl_a3[kwh_cols_a3]
x_a3 = sm.add_constant(x_a3)

y_b1 = ctrl_b1['code']
x_b1 = ctrl_b1[kwh_cols_b1]
x_b1 = sm.add_constant(x_b1)

y_b3 = ctrl_b3['code']
x_b3 = ctrl_b3[kwh_cols_b3]
x_b3 = sm.add_constant(x_b3)

## Run logit
logit_model1 = sm.Logit(y_a1, x_a1) 
logit_results1 = logit_model1.fit() 

logit_model2 = sm.Logit(y_a3, x_a3) 
logit_results2 = logit_model2.fit() 

logit_model3 = sm.Logit(y_b1, x_b1) 
logit_results3 = logit_model3.fit() 

logit_model4 = sm.Logit(y_b3, x_b3) 
logit_results4 = logit_model4.fit() 

print(logit_results1.summary()) 
print(logit_results2.summary()) 
print(logit_results3.summary()) 
print(logit_results4.summary()) 
