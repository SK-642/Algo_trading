import numpy as np 
import pandas as pd
import requests
import math
import creds

stocks=pd.read_csv('sp_500_stocks.csv')
#print(stocks)
def chunks(lst,n):
    for i in range(0,len(lst),n):
        yield(lst[i:i+n])
sym_grp=list(chunks(stocks['Ticker'],100))
#print(len(sym_grp))
#print(type(sym_grp))
sym_str=[]
for i in range(0,len(sym_grp)):
    sym_str.append(','.join(sym_grp[i]))
#print(len(sym_str))
my_columns = ['Ticker','Stock Price','Market Cap','No. of shares to buy']
final_df=pd.DataFrame(columns=my_columns)
#print(final_df)
for sym in sym_str:
    batch_api_call_url = f'https://{creds.workspace}.iex.cloud/v1/data/core/quote/{sym}?token={creds.api_key}'
    data=requests.get(batch_api_call_url).json()
    for index,symbol in enumerate(sym.split(',')):
        #final_df=final_df.append(pd.Series([symbol,data[index]['latestPrice'],data[index]['marketCap'],'N/A'],
        #index=my_columns),ignore_index=True)
        df_new_row = pd.DataFrame({'Ticker':[symbol],'Stock Price':data[index]['latestPrice'],'Market Cap':data[index]['marketCap'],'No. of shares to buy':'N/A'})
        final_df = pd.concat([final_df,df_new_row],ignore_index=True)
#print(final_df)
portfolio_size = input('Enter the value of your portfolio: ')
try:
    val = float(portfolio_size)
except ValueError:
    print('please Enter an Integer')
    portfolio_size = input('Enter the value of your portfolio: ')
position_size = val/len(final_df.index)
#print(position_size)
for i in range(0,len(final_df.index)):
    final_df.loc[i,'No. of shares to buy'] = math.floor(position_size/final_df.loc[i,'Stock Price'])
#final_df.to_csv('Shares_to_Buy.csv')
print(final_df)