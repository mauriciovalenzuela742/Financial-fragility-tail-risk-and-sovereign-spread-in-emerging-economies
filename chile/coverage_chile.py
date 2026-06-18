import pandas as pd
b = pd.read_csv("balance_chile.csv"); b["date"] = pd.to_datetime(b["date"])            
m = b["date"].dt.year >= 2022
for c in ["tot_asset","equity_book","bonds","total_liab","st_borrow","lt_borrow","DP"]:
    b.loc[m, c] = b.loc[m, c] / 1e6
qe = b[b["date"].dt.month.isin([3, 6, 9, 12])].dropna(subset=["tot_asset"]).copy()  # solo cierres de trimestre                       
qe["quarter"] = qe["date"].dt.to_period("Q")                                           
cov = qe.groupby("quarter").agg(n_banks=("bankname", "nunique"), sys_assets=("tot_asset", "sum")).reset_index()                        
cov.to_csv("coverage_chile.csv", index=False)
print(cov.tail())
