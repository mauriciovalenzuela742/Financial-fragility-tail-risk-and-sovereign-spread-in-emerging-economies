import pandas as pd, jloss_common as jc; 
print(jc.reconcile_bonds_vs_rest(pd.read_csv('balance_peru.csv')))