"""
Collects data for gold price and 10-year real yield correlation analysis. Uses yfinance for gold price and FRED (DFII10) for 10-year real yield data. 
The data is saved as CSV, furthermore it returns a sparse version of the data where correlation between two variables are > 0.60, with time periods
for futher analysis. 
"""
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
import sklearn as sci
import matplotlib.pyplot as plt

PATH = Path(__file__).parent
DATA_DIR = PATH / 'data'
GOLD_10Y_CORR_CSV_PATH = DATA_DIR / 'gold_price_real_yield_corr.csv'

ACM_10Y_CSV_PATH = DATA_DIR / 'acm_term_premium_daily.csv'

RAVENPACK_DATASET = PATH / 'ravenpack data'
NODES_CSV_PATH = RAVENPACK_DATASET / 'nodes.csv'
PANEL_CSV_PATH = RAVENPACK_DATASET / 'panel.csv'

START = '2004-01-01'
END = '2026-07-01'

raw_yf = yf.download('GC=F', start=START, end=END, auto_adjust=True)['Close']
raw_fred_10y = pd.read_csv('https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFII10', index_col=0, parse_dates=True, na_values='.')
raw_fred_breakeven = pd.read_csv('https://fred.stlouisfed.org/graph/fredgraph.csv?id=T10YIE', index_col=0, parse_dates=True, na_values='.')

df = pd.concat([raw_yf, raw_fred_10y, raw_fred_breakeven], axis=1, sort=True)
df.dropna(inplace=True)
df.columns = ['Gold Price', '10Y Real Yield', '10Y Breakeven']
df['Log Return Gold Price'] = np.log(df['Gold Price']) - np.log(df['Gold Price'].shift(1))
df['Change 10Y Real Yield'] = df['10Y Real Yield'].diff()
df['Change 10Y Breakeven'] = df['10Y Breakeven'].diff()
# Pearson Correlation, linear relationship between two time series variables
df['Rolling Correlation levels'] = df['Gold Price'].rolling(30).corr(df['10Y Real Yield'])
df['Rolling Correlation logs'] = df['Log Return Gold Price'].rolling(30).corr(df['Change 10Y Real Yield'])
print(df.isna().sum())

df_acm = pd.read_csv(ACM_10Y_CSV_PATH, index_col=0, parse_dates=True, na_values='.')
print(df_acm.index.min(), df_acm.index.max())
df = pd.concat([df, df_acm], axis=1, sort=True)
print(df.isna().sum())
df.dropna(inplace=True)
df.to_csv(DATA_DIR / 'gold_price_real_yield_acm.csv')

df_sparse_levels = df[df['Rolling Correlation levels'].abs() > 0.60]
df_sparse = df_sparse_levels.drop(columns=['acm_tp_level', 'acm_tp_change'])
df_sparse.to_csv(DATA_DIR / 'gold_price_real_yield_corr.csv')

# Deprecated, PowerBI has the same visual
# fig, ax = plt.subplots(figsize=(15,6))
# ax.plot(df.index, df['Rolling Correlation levels'], label='Rolling Corr')
# ax.scatter(df_sparse.index, df_sparse['Rolling Correlation levels'], color='red', s=25, label='Rolling Corr > 0.6')
# ax.set(xlabel='Date', ylabel='Correlation', title='Graph of Corr between Gold Price & 10Y Real Yield')
# ax.legend()
# plt.savefig('rolling_corr_graph.png')
# plt.show()



