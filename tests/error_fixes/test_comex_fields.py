#!/usr/bin/env python3
"""
COMEX銅在庫データの正しいフィールド探索
HG-STX-COMEX の適切な取得方法を調査
"""

import eikon as ek
import json
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ek.set_app_key(config['eikon_api_key'])

ric = 'HG-STX-COMEX'
expected_value = 220954

print(f"=== {ric} フィールド探索テスト ===")
print(f"期待値: {expected_value:,}")

# 各種フィールドパターンをテスト
field_groups = {
    '基本在庫フィールド': ['CF_LAST', 'CF_CLOSE', 'CF_OPEN'],
    '在庫専用フィールド': ['STOCK', 'INVENTORY', 'INVTY', 'STOCKS'],
    '値フィールド': ['VALUE', 'VOLUME', 'AMOUNT'],
    '統計フィールド': ['STAT_VAL', 'GEN_VAL1', 'GEN_VAL2', 'GEN_VAL3'],
    'COMEX特有フィールド': ['WAREHOUSE', 'ELIGIBLE', 'REGISTERED'],
    '取引所フィールド': ['EXCHANGE_STOCK', 'CME_STOCK', 'NYMEX_STOCK'],
    '汎用フィールド': ['LAST', 'CLOSE', 'OPEN', 'VALUE', 'PRICE']
}

successful_fields = []
close_matches = []

for group_name, fields in field_groups.items():
    print(f"\n--- {group_name} ---")
    
    for field in fields:
        try:
            df, err = ek.get_data(ric, [field, 'CF_DATE'])
            
            if err:
                print(f"  ⚠️  {field}: {err}")
            
            if df is not None and not df.empty:
                value = df[field].iloc[0] if field in df.columns else None
                date_val = df['CF_DATE'].iloc[0] if 'CF_DATE' in df.columns else None
                
                if value is not None and str(value) != 'nan' and str(value) != '<NA>':
                    print(f"  ✅ {field}: {value} (日付: {date_val})")
                    successful_fields.append((field, value, date_val))
                    
                    # 期待値との比較
                    try:
                        num_value = float(value)
                        if abs(num_value - expected_value) < 1000:  # 1000以内なら近似
                            print(f"    🎯 期待値に近い！ (差分: {abs(num_value - expected_value):,.0f})")
                            close_matches.append((field, num_value, date_val))
                    except:
                        pass
                else:
                    print(f"  ○ {field}: データなし")
            else:
                print(f"  ❌ {field}: レスポンスなし")
                
        except Exception as e:
            print(f"  ❌ {field}: エラー - {e}")

# 時系列データテスト
print(f"\n=== 時系列データテスト ===")
try:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    ts_data = ek.get_timeseries(
        rics=[ric],
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        interval='daily'
    )
    
    if ts_data is not None and not ts_data.empty:
        print(f"✅ 時系列データ取得成功: {len(ts_data)}日分")
        print("利用可能な列:")
        for col in ts_data.columns:
            latest_val = ts_data[col].iloc[-1] if len(ts_data) > 0 else None
            if latest_val is not None and str(latest_val) != 'nan':
                print(f"  - {col}: {latest_val}")
                
                # 期待値チェック
                try:
                    num_val = float(latest_val)
                    if abs(num_val - expected_value) < 1000:
                        print(f"    🎯 期待値に近い！ (差分: {abs(num_val - expected_value):,.0f})")
                        close_matches.append(('時系列_' + col, num_val, 'latest'))
                except:
                    pass
    else:
        print("❌ 時系列データ取得失敗")
        
except Exception as e:
    print(f"❌ 時系列エラー: {e}")

# 結果サマリー
print(f"\n=== 結果サマリー ===")
print(f"期待値: {expected_value:,}")

if close_matches:
    print("\n🎯 期待値に近いフィールド:")
    for field, value, date_info in close_matches:
        diff = abs(value - expected_value)
        print(f"  - {field}: {value:,.0f} (差分: {diff:,.0f}) [{date_info}]")
else:
    print("\n期待値に近いフィールドなし")

if successful_fields:
    print(f"\n✅ データ取得成功フィールド ({len(successful_fields)}個):")
    for field, value, date_info in successful_fields:
        print(f"  - {field}: {value} [{date_info}]")
else:
    print("\n❌ 有効なフィールドが見つかりませんでした")

print(f"\n=== テスト完了 ===")