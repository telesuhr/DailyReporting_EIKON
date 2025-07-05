#!/usr/bin/env python3
"""
COMEX在庫取得の簡単テスト
実際のレポートシステムと同じ方法で取得
"""

import eikon as ek
import json
import pandas as pd

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ek.set_app_key(config['eikon_api_key'])

# config.jsonから実際のRIC取得
copper_ric = config.get("comex_copper_ric", "")
print(f"設定ファイルのCOMEX RIC: {copper_ric}")

# 実際のレポートと同じ方法でテスト
try:
    fields = ['CF_LAST', 'CF_CLOSE', 'CLOSE']
    
    df, err = ek.get_data(copper_ric, fields)
    
    if err:
        print(f"警告: {err}")
    
    print(f"レスポンス: {df}")
    
    if not df.empty:
        print("✅ データ取得成功!")
        
        # 利用可能な値を順番に試行（レポートと同じロジック）
        total_stock = None
        for field in ['CF_LAST', 'CF_CLOSE', 'CLOSE']:
            if field in df.columns:
                value = df[field].iloc[0]
                print(f"  {field}: {value}")
                if value is not None and not pd.isna(value):
                    total_stock = value
                    print(f"  ✅ 使用値: {field} = {total_stock}")
                    break
        
        if total_stock:
            print(f"\n🎯 COMEX銅在庫: {total_stock:,.0f}トン")
        else:
            print("\n❌ 有効な在庫値なし")
    else:
        print("❌ 空のレスポンス")
        
except Exception as e:
    print(f"❌ エラー: {e}")

print(f"\n期待値: 220,954トン との比較")