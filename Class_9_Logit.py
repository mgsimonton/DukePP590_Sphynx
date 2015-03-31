from __future__ import division
from pandas import Series, DataFrame
from numpy import nan
import pandas as pd
import numpy as np
import statsmodels.api as sm
import os

main_dir = "C:/Users/Daniel/Desktop/BigData/Data"
root = main_dir + "/Class_9"


# IMPORT ----------
# IMPORT ----------

df = pd.read_csv(root + "/allocation_subsamp.csv", names = ['ID', 'code', 'tariff', 'stimulus'])



## 1. CREATE 4 UNIQUE VECTORS USING ALLOCATION DATA ----------
## 1. CREATE 4 UNIQUE VECTORS USING ALLOCATION DATA ----------

# Separate 1 control and 4 treatment groups
ctr = df[(df.tariff == 'E')]
ctr_id = ctr.ID.values
trta1 = df[(df.tariff == 'A') & (df.stimulus == '1')]
trta1_id = trta1.ID.values
trta3 = df[(df.tariff == 'A') & (df.stimulus == '3')]
trta3_id = trta3.ID.values
trtb1 = df[(df.tariff == 'B') & (df.stimulus == '1')]
trtb1_id = trtb1.ID.values
trtb3 = df[(df.tariff == 'B') & (df.stimulus == '3')]
trtb3_id = trtb3.ID.values



## 2. SET RANDOM SEED TO 1789 ----------
## 2. SET RANDOM SEED TO 1789 ----------

np.random.seed(1789)



## 3. EXTRACT SAMPLE SIZES WITHOUT REPLACEMENT ----------
## 3. EXTRACT SAMPLE SIZES WITHOUT REPLACEMENT ----------

ctr_samp = np.random.choice(ctr_id, size=300, replace=False)
trta1_samp = np.random.choice(trta1_id, size=150, replace=False)
trta3_samp = np.random.choice(trta3_id, size=150, replace=False)
trtb1_samp = np.random.choice(trtb1_id, size=50, replace=False)
trtb3_samp = np.random.choice(trtb3_id, size=50, replace=False)



## 4. CREATE DATAFRAME WITH SAMPLED IDs ----------
## 4. CREATE DATAFRAME WITH SAMPLED IDs ----------

# Convert each series in dataframe with 'ID' column header
df_ctr = pd.DataFrame(ctr_samp, columns=['ID'])
df_trta1 = pd.DataFrame(trta1_samp, columns=['ID'])
df_trta3 = pd.DataFrame(trta3_samp, columns=['ID'])
df_trtb1 = pd.DataFrame(trtb1_samp, columns=['ID'])
df_trtb3 = pd.DataFrame(trtb3_samp, columns=['ID'])

# Vertically merge multiple dataframes into single dataframe
df_samp = df_ctr.append(df_trta1)
df_samp = df_samp.append(df_trta3)
df_samp = df_samp.append(df_trtb1)
df_samp = df_samp.append(df_trtb3)
df_samp = df_samp.reset_index()

df_samp.head()
# has unnecessary index column
df_samp.drop([df_samp.columns[0]], axis=1, inplace=True)
# unnecessary index column is dropped



## 5. MERGE SAMPLED IDs WITH CONSUMPTION DATA ----------
## 5. MERGE SAMPLED IDs WITH CONSUMPTION DATA ----------

# Import consumption data
df1 = pd.read_csv(root + "/kwh_redux_pretrial.csv", sep=",", parse_dates=[2], date_parser=np.datetime64)

# Check data type of sampled ids and redux data
df_samp['ID'].dtype
# returns 0
df1['ID'].dtype
# returns int64. 

# Convert sampled IDs to numeric before immediate merger
df_samp = df_samp.apply(int64, inplace=True)

# Convert allocation IDs to numeric for later merger; drop unnecessary row.
df['ID'] = df['ID'].convert_objects(convert_numeric=True)
df.drop(df.index[[0]], inplace=True)



## 6. MERGE SAMPLED IDs AND CONSUMPTION DATA ----------
## 6. MERGE SAMPLED IDs AND CONSUMPTION DATA ----------

df2 = pd.merge(df_samp, df1, on='ID')



## 7. AGGREGATE ALL CONSUMPTION DATA 'BY MONTH' FOR EACH SEPARATE 'GROUP'
## 7. AGGREGATE ALL CONSUMPTION DATA 'BY MONTH' FOR EACH SEPARATE 'GROUP'

# Break out 'month' variable; delete unnecessaries
df2['month'] = df2['date'].apply(lambda x: x.month)
df2.drop(['date','hour', 'minute'],1,inplace=True)

# sum monthly consumption for each sampled ID
grp = df2.groupby(['ID', 'month',])
df2 = grp['kwh'].sum().reset_index()



## 8. PIVOT DATA FROM LONG TO WIDE, SO KWH FOR EACH MONTH IS A VARIABLE
## 8. PIVOT DATA FROM LONG TO WIDE, SO KWH FOR EACH MONTH IS A VARIABLE

# Create kwh_month column
df2.month.dtype
df2['mo_str'] = ['0' + str(v) if v <13 else str(v) for v in df2['month']]
df2['kwh_mo'] = 'kwh_' + df2.mo_str.apply(str)

# pivot DF so kwh_month values become 5 columns, each column includes kwh consumption
# for each sampled ID in that given month
df_piv = df2.pivot('ID','kwh_mo','kwh')
df_piv.reset_index(inplace = True)
df_piv.columns.name = None



## 9. MERGE THE WIDE DATASET WITH THE TREATMENT DATA
## 9. MERGE THE WIDE DATASET WITH THE TREATMENT DATA

df = pd.merge(df_piv, df, on='ID')



## 10. COMPUTE LOGIT MODEL COMPARING EACH TREATMENT TO THE CONTROL USING CONS. DATA
## 10. COMPUTE LOGIT MODEL COMPARING EACH TREATMENT TO THE CONTROL USING CONS. DATA

# Rename 'code' values to distinguish between different trt/ctl groups
df.loc[(df.tariff == 'E'), 'code'] = 1
df.loc[(df.tariff == 'A') & (df.stimulus == '1'), 'code'] = 2
df.loc[(df.tariff == 'A') & (df.stimulus == '3'), 'code'] = 3
df.loc[(df.tariff == 'B') & (df.stimulus == '1'), 'code'] = 4
df.loc[(df.tariff == 'B') & (df.stimulus == '3'), 'code'] = 5

# Break out 'code' values into individual dummy columns for each trt/ctl group
df1 = pd.get_dummies(df, columns = ['code'])

df1.loc[(df1.code_2 == 0), 'code_2'] = nan
df1.loc[df1.code_1 == 1, 'code_2'] = 0
df1.loc[(df1.code_3 == 0), 'code_3'] = nan
df1.loc[df1.code_1 == 1, 'code_3'] = 0
df1.loc[(df1.code_4 == 0), 'code_4'] = nan
df1.loc[df1.code_1 == 1, 'code_4'] = 0
df1.loc[(df1.code_5 == 0), 'code_5'] = nan
df1.loc[df1.code_1 == 1, 'code_5'] = 0

# Rename trt/ctl group columns so meanings are more clear
df1.rename(columns={'code_1': 'ctl', 'code_2': 'trt1', 'code_3': 'trt2', 'code_4': 'trt3', 'code_5': 'trt4'}, inplace=True)

# Break out each trt group into individual DF to allow for easier logit modeling
# Reason - so logit model doesn't have to deal with NaN values
df_trt1 = df1[df1.trt1 >= 0]
df_trt2 = df1[df1.trt2 >= 0]
df_trt3 = df1[df1.trt3 >= 0]
df_trt4 = df1[df1.trt4 >= 0]

# aggregate columns into single variable
kwh_cols2 = [v for v in df_trt1.columns.values if v.startswith('kwh')]
kwh_cols3 = [v for v in df_trt2.columns.values if v.startswith('kwh')]
kwh_cols4 = [v for v in df_trt3.columns.values if v.startswith('kwh')]
kwh_cols5 = [v for v in df_trt4.columns.values if v.startswith('kwh')]

# Set up Y,X for 4 treatment group analysis
Y1 = df_trt1['trt1']
X1 = df_trt1[kwh_cols2]
X1 = sm.add_constant(X1)

Y2 = df_trt2['trt2']
X2 = df_trt2[kwh_cols3]
X2 = sm.add_constant(X2)

Y3 = df_trt3['trt3']
X3 = df_trt3[kwh_cols4]
X3 = sm.add_constant(X3)

Y4 = df_trt4['trt4']
X4 = df_trt4[kwh_cols5]
X4 = sm.add_constant(X4)




# Logit analysis for each treatment group
logit_model1 = sm.Logit(Y1, X1)
logit_results1 = logit_model1.fit()

logit_model2 = sm.Logit(Y2, X2)
logit_results2 = logit_model2.fit()

logit_model3 = sm.Logit(Y3, X3)
logit_results3 = logit_model3.fit()

logit_model4 = sm.Logit(Y4, X4)
logit_results4 = logit_model4.fit()

print(logit_results1.summary())
print(logit_results2.summary())
print(logit_results3.summary())
print(logit_results4.summary())


