#!/usr/bin/env python3
"""US10YT=RRの詳細フィールドテスト"""

import eikon as ek
import json

with open('config.json', 'r') as f:
    config = json.load(f)
ek.set_app_key(config['eikon_api_key'])

print('=== US10YT=RR 詳細フィールドテスト ===')
fields = ['CF_LAST', 'CF_CLOSE', 'BID', 'ASK', 'YIELD', 'YLD_1', 'YIELDTOWORST', 'SECTYPE']
df, err = ek.get_data('US10YT=RR', fields)

if err:
    print(f'警告: {err}')

if df is not None and not df.empty:
    print("\n取得できたフィールド:")
    for col in df.columns:
        value = df[col].iloc[0]
        if value is not None and str(value) != 'nan':
            print(f'  {col}: {value}')

# 時系列データテスト
print('\n=== 時系列データテスト ===')
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=10)

df_ts = ek.get_timeseries(
    rics=['US10YT=RR'],
    start_date=start_date.strftime('%Y-%m-%d'),
    end_date=end_date.strftime('%Y-%m-%d'),
    interval='daily'
)

if df_ts is not None and not df_ts.empty:
    print(f'時系列データ取得成功: {len(df_ts)}日分')
    print(df_ts.tail(3))
else:
    print('時系列データ取得失敗')