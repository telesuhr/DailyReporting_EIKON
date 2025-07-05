#!/usr/bin/env python3
"""
中国鉱工業生産指数のテスト
aCNIACT/C vs 既存のCNIPY=ECI比較
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
test_rics = {
    'aCNIACT/C': '中国鉱工業生産指数（新候補）',
    'CNIPY=ECI': '現在設定（エラー確認）',
    'CHIPTOT.H': '前回テスト（工業生産指数）'
}

print("=== 中国鉱工業生産指数テスト ===")

for ric, description in test_rics.items():
    print(f"\n--- {ric} ({description}) ---")
    
    try:
        df, err = ek.get_data(ric, ['CF_LAST', 'CF_CLOSE', 'CF_DATE', 'PCTCHNG'])
        
        if err:
            print(f"  警告: {err}")
        
        if df is not None and not df.empty:
            print("  ✅ データ取得成功!")
            
            for col in df.columns:
                value = df[col].iloc[0]
                if value is not None and str(value) != 'nan':
                    print(f"    {col}: {value}")
            
            # 値の妥当性チェック（工業生産指数は通常-20%〜+30%程度）
            if 'CF_LAST' in df.columns:
                last_value = df['CF_LAST'].iloc[0]
                if last_value is not None:
                    if -30 <= last_value <= 50:
                        print(f"    ✅ 値が妥当範囲内: {last_value}")
                    else:
                        print(f"    ⚠️  値要確認: {last_value}")
                        
        else:
            print("  ❌ データなし")
            
    except Exception as e:
        print(f"  ❌ エラー: {e}")

print("\n=== テスト完了 ===")