#!/usr/bin/env python3
"""
金価格取得テストとCopper/Gold Ratio計算
XAU= で金価格を取得し、LME銅価格との比率を計算
"""

import eikon as ek
import json
import warnings

warnings.filterwarnings('ignore')

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ek.set_app_key(config['eikon_api_key'])

print("=== 金価格取得テスト ===")

# 金価格テスト
gold_ric = 'XAU='
print(f"金価格RIC: {gold_ric}")

try:
    fields = ['CF_LAST', 'CF_CLOSE', 'CF_DATE', 'PCTCHNG']
    df_gold, err = ek.get_data(gold_ric, fields)
    
    if err:
        print(f"警告: {err}")
    
    if df_gold is not None and not df_gold.empty:
        print("✅ 金価格取得成功!")
        
        gold_price = None
        for field in ['CF_LAST', 'CF_CLOSE']:
            if field in df_gold.columns:
                value = df_gold[field].iloc[0]
                if value is not None and str(value) != 'nan' and str(value) != '<NA>':
                    gold_price = value
                    print(f"  {field}: ${value:.2f}/oz")
                    break
        
        if 'CF_DATE' in df_gold.columns:
            print(f"  日付: {df_gold['CF_DATE'].iloc[0]}")
        
        if 'PCTCHNG' in df_gold.columns:
            pct_change = df_gold['PCTCHNG'].iloc[0]
            if pct_change is not None and str(pct_change) != 'nan':
                print(f"  日次変化: {pct_change:.2f}%")
    else:
        print("❌ 金価格取得失敗")
        gold_price = None
        
except Exception as e:
    print(f"❌ 金価格エラー: {e}")
    gold_price = None

# LME銅価格取得
print(f"\n=== LME銅価格取得 ===")
copper_ric = config['metals_rics']['Copper']  # CMCU3
print(f"銅価格RIC: {copper_ric}")

try:
    df_copper, err = ek.get_data(copper_ric, fields)
    
    if err:
        print(f"警告: {err}")
    
    if df_copper is not None and not df_copper.empty:
        print("✅ 銅価格取得成功!")
        
        copper_price = None
        for field in ['CF_LAST', 'CF_CLOSE']:
            if field in df_copper.columns:
                value = df_copper[field].iloc[0]
                if value is not None and str(value) != 'nan' and str(value) != '<NA>':
                    copper_price = value
                    print(f"  {field}: ${value:.2f}/MT")
                    break
    else:
        print("❌ 銅価格取得失敗")
        copper_price = None
        
except Exception as e:
    print(f"❌ 銅価格エラー: {e}")
    copper_price = None

# Copper/Gold Ratio計算
print(f"\n=== Copper/Gold Ratio計算 ===")

if gold_price and copper_price:
    # 単位調整: 銅(USD/MT) ÷ 金(USD/oz)
    # 1MT = 32,150.7 oz なので、比率を正規化
    # 通常のCopper/Gold Ratioは銅価格(セント/ポンド) ÷ 金価格(USD/oz)で計算
    
    # 銅価格をセント/ポンドに変換: USD/MT → セント/ポンド
    # 1MT = 2,204.62ポンド, 1USD = 100セント
    copper_cents_per_lb = (copper_price * 100) / 2204.62
    
    # Copper/Gold Ratio = 銅価格(セント/ポンド) ÷ 金価格(USD/oz)
    ratio = copper_cents_per_lb / gold_price
    
    print(f"銅価格: ${copper_price:.2f}/MT = {copper_cents_per_lb:.2f}セント/ポンド")
    print(f"金価格: ${gold_price:.2f}/oz")
    print(f"🎯 Copper/Gold Ratio: {ratio:.4f}")
    
    # 妥当性チェック（通常0.1-0.6程度）
    if 0.05 <= ratio <= 1.0:
        print(f"✅ 比率が妥当範囲内")
    else:
        print(f"⚠️  比率要確認（通常0.1-0.6程度）")
    
    # 計算用関数の提案
    print(f"\n=== 実装コード例 ===")
    print(f"""
def calculate_copper_gold_ratio(copper_usd_per_mt, gold_usd_per_oz):
    \"\"\"Copper/Gold Ratio計算\"\"\"
    # 銅価格をセント/ポンドに変換
    copper_cents_per_lb = (copper_usd_per_mt * 100) / 2204.62
    
    # 比率計算
    ratio = copper_cents_per_lb / gold_usd_per_oz
    return ratio

# 現在値での計算例
ratio = calculate_copper_gold_ratio({copper_price:.2f}, {gold_price:.2f})
print(f"Copper/Gold Ratio: {{ratio:.4f}}")
""")
    
else:
    print("❌ 価格データ不足のため比率計算不可")
    if not gold_price:
        print("  - 金価格取得失敗")
    if not copper_price:
        print("  - 銅価格取得失敗")

print(f"\n=== テスト完了 ===")