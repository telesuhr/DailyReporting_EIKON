#!/usr/bin/env python3
"""
SHFE在庫とSMM在庫データの包括的検証
各RICと適切なフィールドを探索
"""

import eikon as ek
import json
import pandas as pd
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ek.set_app_key(config['eikon_api_key'])

def test_inventory_ric(ric, description, expected_range=None):
    """在庫RICの包括的テスト"""
    print(f"\n--- {ric} ({description}) ---")
    
    # 基本フィールドテスト
    basic_fields = ['CF_LAST', 'CF_CLOSE', 'CF_DATE']
    
    try:
        df, err = ek.get_data(ric, basic_fields)
        
        if err:
            print(f"  警告: {err}")
        
        if df is not None and not df.empty:
            print("  📊 基本データ:")
            has_valid_data = False
            
            for col in df.columns:
                if col != 'Instrument':
                    value = df[col].iloc[0]
                    if value is not None and str(value) != 'nan' and str(value) != '<NA>':
                        print(f"    {col}: {value}")
                        has_valid_data = True
                    else:
                        print(f"    {col}: <データなし>")
            
            if has_valid_data:
                # 在庫値の妥当性チェック
                stock_value = None
                if 'CF_LAST' in df.columns:
                    stock_value = df['CF_LAST'].iloc[0]
                elif 'CF_CLOSE' in df.columns:
                    stock_value = df['CF_CLOSE'].iloc[0]
                
                if stock_value is not None and str(stock_value) != 'nan' and str(stock_value) != '<NA>':
                    try:
                        num_value = float(stock_value)
                        if expected_range:
                            min_val, max_val = expected_range
                            if min_val <= num_value <= max_val:
                                print(f"    ✅ 在庫値妥当: {num_value:,.0f}トン")
                            else:
                                print(f"    ⚠️  在庫値要確認: {num_value:,.0f}トン (期待範囲: {min_val:,}-{max_val:,})")
                        else:
                            print(f"    📈 在庫値: {num_value:,.0f}トン")
                    except:
                        print(f"    ⚠️  数値変換不可: {stock_value}")
                
                # 時系列データテスト
                print(f"  📈 時系列データテスト:")
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
                        print(f"    ✅ 時系列取得成功: {len(ts_data)}日分")
                        if 'CLOSE' in ts_data.columns:
                            latest = ts_data['CLOSE'].iloc[-1]
                            if latest is not None and str(latest) != 'nan':
                                print(f"    最新値: {latest:,.0f}トン")
                    else:
                        print(f"    ⚠️  時系列データなし")
                        
                except Exception as ts_e:
                    print(f"    ❌ 時系列エラー: {ts_e}")
                
                return True  # 成功
            else:
                print(f"    ○ RIC有効だが有効データなし")
                return False
        else:
            print(f"    ❌ レスポンスなし")
            return False
            
    except Exception as e:
        print(f"    ❌ エラー: {e}")
        return False

# SHFE在庫データテスト
print("=== SHFE在庫データ検証 ===")
shfe_inventory_rics = config.get("shfe_inventory_rics", {})
shfe_results = {}

# SHFE在庫の期待値範囲（トン）
shfe_expected_ranges = {
    'Copper': (50000, 500000),    # 銅: 5万-50万トン
    'Aluminium': (100000, 1000000), # アルミ: 10万-100万トン
    'Zinc': (20000, 300000),      # 亜鉛: 2万-30万トン
    'Lead': (10000, 200000),      # 鉛: 1万-20万トン
    'Nickel': (5000, 100000),     # ニッケル: 5千-10万トン
    'Tin': (1000, 50000)          # スズ: 1千-5万トン
}

for metal_name, ric in shfe_inventory_rics.items():
    expected_range = shfe_expected_ranges.get(metal_name)
    success = test_inventory_ric(ric, f"SHFE {metal_name} 在庫", expected_range)
    shfe_results[metal_name] = success

# SMM在庫データテスト
print(f"\n=== SMM在庫データ検証 ===")
smm_inventory_rics = config.get("smm_inventory_rics", {})
smm_results = {}

# SMM在庫の期待値範囲（トン）
smm_expected_ranges = {
    'Copper': (10000, 200000),    # 銅: 1万-20万トン
    'Aluminium': (50000, 500000), # アルミ: 5万-50万トン
    'Zinc': (5000, 100000)        # 亜鉛: 5千-10万トン
}

for metal_name, ric in smm_inventory_rics.items():
    expected_range = smm_expected_ranges.get(metal_name)
    success = test_inventory_ric(ric, f"SMM {metal_name} 在庫", expected_range)
    smm_results[metal_name] = success

# 結果サマリー
print(f"\n=== 結果サマリー ===")

print(f"\n📊 SHFE在庫データ:")
shfe_success_count = sum(shfe_results.values())
print(f"  成功: {shfe_success_count}/{len(shfe_results)} 金属")
for metal, success in shfe_results.items():
    status = "✅" if success else "❌"
    print(f"    {status} {metal}: {shfe_inventory_rics[metal]}")

print(f"\n📊 SMM在庫データ:")
smm_success_count = sum(smm_results.values())
print(f"  成功: {smm_success_count}/{len(smm_results)} 金属")
for metal, success in smm_results.items():
    status = "✅" if success else "❌"
    print(f"    {status} {metal}: {smm_inventory_rics[metal]}")

# 総括
total_success = shfe_success_count + smm_success_count
total_tests = len(shfe_results) + len(smm_results)
print(f"\n🎯 全体結果: {total_success}/{total_tests} RIC成功")

if total_success == 0:
    print("❌ すべての在庫データが取得不可")
elif total_success == total_tests:
    print("✅ すべての在庫データ取得成功！")
else:
    print("⚠️  一部の在庫データのみ利用可能")

print(f"\n=== テスト完了 ===")