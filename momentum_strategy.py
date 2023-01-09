import numpy as np
import pandas as pd
import requests
import math
from scipy import stats
import creds1
from statistics import mean

stocks=pd.read_csv('sp_500_stocks.csv')
def chunks(lst,n):
    for i in range(0,len(lst),n):
        yield(lst[i:i+n])
sym_grp=list(chunks(stocks['Ticker'],100))

sym_str=[]
for i in range(0,len(sym_grp)):
    sym_str.append(','.join(sym_grp[i]))

my_columns = ['Ticker','Price','One year price return','One year return percentile','Six month price return','Six month return percentile',
'Three month price return','Three month return percentile','One month price return','One month return percentile',
'momentum score','No. of shares to buy']

#momentum score is given by average of momentum percentile scores

momentum_df = pd.DataFrame(columns = my_columns)
for sym in sym_str:
    batch_api_call_url = f'https://cloud.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={sym}&token={creds1.api_key}'
    data=requests.get(batch_api_call_url).json()
    for symbol in sym.split(','):
        df_new_row = pd.DataFrame({'Ticker':[symbol],'Price':data[symbol]['quote']['latestPrice'],'One year price return':
        data[symbol]['stats']['year1ChangePercent'],'One year return percentile':'N/A','Six month price return':
        data[symbol]['stats']['month6ChangePercent'],'Six month return percentile':'N/A','Three month price return':
        data[symbol]['stats']['month3ChangePercent'],'Three month return percentile':'N/A','One month price return':
        data[symbol]['stats']['month1ChangePercent'],'One month return percentile':'N/A','momentum score':'N/A','No. of shares to buy':'N/A'})
        momentum_df = pd.concat([momentum_df,df_new_row],ignore_index=True)

time_periods=['One year','Six month','Three month','One month']
for row in momentum_df.index:
    momentum_percentile =[]
    for tp in time_periods:
        change_col=f'{tp} price return'
        percentile_col = f'{tp} return percentile'
        momentum_df.loc[row,percentile_col] = stats.percentileofscore(momentum_df[change_col],momentum_df.loc[row,change_col])
        momentum_percentile.append(momentum_df.loc[row,f'{tp} return percentile'])
    momentum_df.loc[row,'momentum score'] = mean(momentum_percentile)
momentum_df.sort_values('momentum score', ascending = False, inplace = True)
momentum_df = momentum_df[:50]
momentum_df.reset_index(drop = True,inplace = True)

portfolio_size = input('Enter the value of your portfolio: ')
try:
    val = float(portfolio_size)
except ValueError:
    print('please Enter an Integer')
    portfolio_size = input('Enter the value of your portfolio: ')
position_size = val/len(momentum_df.index)

for i in range(0,len(momentum_df.index)):
    momentum_df.loc[i,'No. of shares to buy'] = math.floor(position_size/momentum_df.loc[i,'Price'])

print(momentum_df)

momentum_df.to_csv('top50shares2buy.csv')
