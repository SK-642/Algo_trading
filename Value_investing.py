import numpy as np
import pandas as pd
import requests
import math
from scipy import stats
import creds2
from statistics import mean

stocks=pd.read_csv('sp_500_stocks.csv')
def chunks(lst,n):
    for i in range(0,len(lst),n):
        yield(lst[i:i+n])
sym_grp=list(chunks(stocks['Ticker'],100))

sym_str=[]
for i in range(0,len(sym_grp)):
    sym_str.append(','.join(sym_grp[i]))

my_columns = ['Ticker','Price','PE ratio','PE ratio percentile','Price to book ratio','P2B percentile',
'Price to sales ratio','P2S percentile','EV/EBITDA','EV/EBITDA percentile',
'EV/GP','EV/GP percentile','rv score','No. of shares to buy']

rv_df=pd.DataFrame(columns=my_columns)

for sym in sym_str:
    batch_api_call_url = f'https://cloud.iexapis.com/stable/stock/batch/?symbols={sym}&types=quote,advanced-stats&token={creds2.api_key}'
    data=requests.get(batch_api_call_url).json()

    for symbol in sym.split(','):
        enterprise_value = data[symbol]['advanced-stats']['enterpriseValue']
        ebitda = data[symbol]['advanced-stats']['EBITDA']
        gross_profit = data[symbol]['advanced-stats']['grossProfit']
        
        try:
            ev_to_ebitda = enterprise_value/ebitda
        except TypeError:
            ev_to_ebitda = np.NaN
        
        try:
            ev_to_gross_profit = enterprise_value/gross_profit
        except TypeError:
            ev_to_gross_profit = np.NaN
            
        df_new_row = pd.DataFrame({'Ticker':[symbol],'Price':data[symbol]['quote']['latestPrice'],'PE ratio':
        data[symbol]['quote']['peratio'],'PE ratio percentile':'N/A','Price to book ratio':
        data[symbol]['advanced-stats']['priceToBook'],'P2B percentile':'N/A','Price to sales ratio':
        data[symbol]['advanced-stats']['priceToSales'],'P2S percentile':'N/A','EV/EBITDA':
        ev_to_ebitda,'EV/EBITDA percentile':'N/A','EV/GP':ev_to_gross_profit,
        'EV/GP percentile':'N/A','rv score':'N/A','No. of shares to buy':'N/A'})
        rv_df = pd.concat([rv_df,df_new_row],ignore_index=True)
    
for column in ['PE ratio', 'Price to book ratio','Price to sales ratio',  'EV/EBITDA','EV/GP']:
    rv_df[column].fillna(rv_df[column].mean(), inplace = True)
#print(rv_df[rv_df.isnull().any(axis=1)])


metrics = {'Price-to-Earnings Ratio': 'PE Percentile','Price-to-Book Ratio':'PB Percentile','Price-to-Sales Ratio': 'PS Percentile',
            'EV/EBITDA':'EV/EBITDA Percentile','EV/GP':'EV/GP Percentile'}

for row in rv_df.index:
    for metric in metrics.keys():
        rv_df.loc[row, metrics[metric]] = stats.percentileofscore(rv_df[metric], rv_df.loc[row, metric])

for row in rv_df.index:
    value_percentiles = []
    for metric in metrics.keys():
        value_percentiles.append(rv_df.loc[row, metrics[metric]])
    rv_df.loc[row, 'rv Score'] = mean(value_percentiles)

rv_df.sort_values('rv score', ascending = False, inplace = True)
rv_df = rv_df[:50]
rv_df.reset_index(drop = True,inplace = True)

portfolio_size = input('Enter the value of your portfolio: ')
try:
    val = float(portfolio_size)
except ValueError:
    print('please Enter an Integer')
    portfolio_size = input('Enter the value of your portfolio: ')
position_size = val/len(rv_df.index)

for i in range(0,len(rv_df.index)):
    rv_df.loc[i,'No. of shares to buy'] = math.floor(position_size/rv_df.loc[i,'Price'])

print(rv_df)
rv_df.to_csv('top50shares2buy_by_value.csv')