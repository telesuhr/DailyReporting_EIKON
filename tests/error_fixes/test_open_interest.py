#!/usr/bin/env python3
"""
建玉（Open Interest）フィールドの動作確認テスト
OPINT_1フィールドが正しく取得できるかを確認
"""

import eikon as ek
import json
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# config.jsonから設定読み込み
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# EIKON API初期化
ek.set_app_key(config['eikon_api_key'])

# テスト対象の金属とRIC
test_metals = {
    'Copper': 'CMCU3',
    'Aluminium': 'CMAL3',
    'Zinc': 'CMZN3',
    'Lead': 'CMPB3',
    'Nickel': 'CMNI3',
    'Tin': 'CMSN3'
}

print(f"=== 建玉（Open Interest）フィールドテスト ===")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 各金属で建玉データを取得テスト
for metal_name, ric in test_metals.items():
    print(f"--- {metal_name} ({ric}) ---")
    
    try:
        # OPINT_1フィールドで建玉を取得
        fields = ['CF_LAST', 'OPINT_1', 'CF_DATE']
        df, err = ek.get_data(ric, fields)
        
        if err:
            print(f"  警告: {err}")
        
        if df is not None and not df.empty:
            print(f"  最終価格: {df['CF_LAST'].iloc[0]}")
            
            # OPINT_1の値を確認
            if 'OPINT_1' in df.columns:
                oi_value = df['OPINT_1'].iloc[0]
                if oi_value is not None and str(oi_value) != 'nan':
                    print(f"  建玉 (OPINT_1): {oi_value:,.0f} 契約")
                else:
                    print(f"  建玉 (OPINT_1): データなし")
            else:
                print(f"  建玉 (OPINT_1): フィールドが存在しない")
                
            print(f"  データ日付: {df['CF_DATE'].iloc[0]}")
        else:
            print(f"  エラー: データ取得失敗")
    
    except Exception as e:
        print(f"  エラー: {e}")
    
    print()

print("\n=== 代替フィールドのテスト ===")
# 念のため他の候補フィールドもテスト
alternative_fields = ['OPEN_INT', 'OI_VALUE_1', 'CF_OI', 'OPENINTEREST']

for field_name in alternative_fields:
    print(f"\n--- {field_name}フィールドのテスト (銅のみ) ---")
    try:
        df, err = ek.get_data('CMCU3', ['CF_LAST', field_name])
        
        if err:
            print(f"  警告: {err}")
            
        if df is not None and not df.empty and field_name in df.columns:
            value = df[field_name].iloc[0]
            if value is not None and str(value) != 'nan':
                print(f"  {field_name}: {value}")
            else:
                print(f"  {field_name}: データなし")
        else:
            print(f"  {field_name}: フィールドが存在しない")
            
    except Exception as e:
        print(f"  エラー: {e}")

print("\n=== テスト完了 ===")