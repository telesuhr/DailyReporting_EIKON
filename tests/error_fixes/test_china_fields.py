#!/usr/bin/env python3
"""
中国鉱工業生産指数 - 各種フィールドテスト
RICは有効だがフィールド指定の問題の可能性を調査
"""

import eikon as ek
import json
import warnings

warnings.filterwarnings('ignore')

# config.jsonから設定読み込み
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# EIKON API初期化
ek.set_app_key(config['eikon_api_key'])

# テスト対象RIC
test_ric = 'aCNIACT/C'
print(f"=== {test_ric} フィールド探索テスト ===")

# 様々なフィールドパターンをテスト
field_groups = {
    '基本価格フィールド': ['CF_LAST', 'CF_CLOSE', 'CF_OPEN'],
    '値フィールド': ['VALUE', 'VALUE_TS', 'VALUE.Value'],
    '統計フィールド': ['STAT_VAL', 'STATISTIC', 'INDEX_VAL'],
    '経済指標フィールド': ['ECON_VAL', 'INDICATOR', 'ECONOMIC_DATA'],
    'カスタムフィールド': ['GEN_VAL1', 'GEN_VAL2', 'GEN_VAL3'],
    '時系列フィールド': ['CLOSE', 'LAST', 'VALUE'],
    '汎用フィールド': ['PRICE', 'RATE', 'INDEX']
}

successful_fields = []

for group_name, fields in field_groups.items():
    print(f"\n--- {group_name} ---")
    
    for field in fields:
        try:
            df, err = ek.get_data(test_ric, [field, 'CF_DATE'])
            
            if df is not None and not df.empty:
                value = df[field].iloc[0] if field in df.columns else None
                if value is not None and str(value) != 'nan' and str(value) != '<NA>':
                    print(f"  ✅ {field}: {value}")
                    successful_fields.append((field, value))
                else:
                    print(f"  ○ {field}: データなし")
            else:
                print(f"  ❌ {field}: レスポンスなし")
                
        except Exception as e:
            print(f"  ❌ {field}: {e}")

# 時系列データでのテスト
print(f"\n=== 時系列データテスト ===")
try:
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    ts_data = ek.get_timeseries(
        rics=[test_ric],
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
    else:
        print("❌ 時系列データ取得失敗")
        
except Exception as e:
    print(f"❌ 時系列エラー: {e}")

# 結果サマリー
print(f"\n=== 結果サマリー ===")
if successful_fields:
    print("✅ 使用可能フィールド:")
    for field, value in successful_fields:
        print(f"  - {field}: {value}")
else:
    print("❌ 有効なフィールドが見つかりませんでした")

print(f"\n推奨: 時系列データが成功した場合、get_timeseries()を使用してください")