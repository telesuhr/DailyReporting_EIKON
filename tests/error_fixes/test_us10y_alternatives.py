#!/usr/bin/env python3
"""
米国10年債利回りの代替RICテスト
US10YT=RRを含む各種候補の動作確認
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

# テスト対象の米国10年債利回りRIC
us10y_alternatives = {
    # 現在エラーのRIC
    'TNX': 'US 10-Year Treasury Note Yield (Current)',
    
    # 候補RIC
    'US10YT=RR': 'US 10-Year Treasury (Reuters)',
    'US10Y=TWEB': 'US 10-Year Treasury (TWEB)',
    '.TNX': 'US 10-Year Treasury (Dot Version)',
    'USGG10YR': 'US Government 10-Year',
    'DGS10': 'US Treasury 10-Year Constant Maturity',
    'US10YT=': 'US 10-Year Treasury (Alternative)',
    'USDCRRT10Y=': 'USD Credit Risk Free 10Y',
    'IRUS10=RR': 'USD Interest Rate Swap 10Y',
    'US10Y=X': 'US 10-Year Alternative Exchange',
}

print(f"=== 米国10年債利回り代替RICテスト ===")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 各RICをテスト
successful_rics = []
failed_rics = []

for ric, description in us10y_alternatives.items():
    print(f"--- {ric} ({description}) ---")
    
    try:
        # 基本的なフィールドで取得テスト
        fields = ['CF_LAST', 'CF_CLOSE', 'PCTCHNG', 'CF_DATE']
        df, err = ek.get_data(ric, fields)
        
        if err:
            print(f"  警告: {err}")
            
        if df is not None and not df.empty:
            # 少なくとも1つの有効な値があるかチェック
            has_valid_data = False
            
            for field in ['CF_LAST', 'CF_CLOSE']:
                if field in df.columns:
                    value = df[field].iloc[0]
                    if value is not None and str(value) != 'nan':
                        print(f"  {field}: {value:.4f}%")
                        has_valid_data = True
                        break
            
            if has_valid_data:
                if 'PCTCHNG' in df.columns and df['PCTCHNG'].iloc[0] is not None:
                    pct_change = df['PCTCHNG'].iloc[0]
                    if str(pct_change) != 'nan':
                        print(f"  日次変化: {pct_change:.4f}%")
                
                if 'CF_DATE' in df.columns:
                    print(f"  データ日付: {df['CF_DATE'].iloc[0]}")
                
                successful_rics.append((ric, description, value))
                print(f"  ✅ 成功: データ取得可能")
            else:
                failed_rics.append((ric, description, "データなし"))
                print(f"  ❌ 失敗: 有効なデータなし")
        else:
            failed_rics.append((ric, description, "空のレスポンス"))
            print(f"  ❌ 失敗: 空のレスポンス")
            
    except Exception as e:
        failed_rics.append((ric, description, str(e)))
        print(f"  ❌ エラー: {e}")
    
    print()

# 結果サマリー
print("\n=== 結果サマリー ===")
print(f"\n✅ 成功したRIC ({len(successful_rics)}個):")
for ric, desc, value in successful_rics:
    print(f"  - {ric}: {desc} (利回り: {value:.4f}%)")

print(f"\n❌ 失敗したRIC ({len(failed_rics)}個):")
for ric, desc, reason in failed_rics:
    print(f"  - {ric}: {desc} ({reason})")

# 時系列データのテスト（成功したRICのみ）
if successful_rics:
    print("\n=== 時系列データテスト（成功RICのみ） ===")
    test_ric = successful_rics[0][0]
    print(f"\nテストRIC: {test_ric}")
    
    try:
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        df_ts = ek.get_timeseries(
            rics=[test_ric],
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            interval='daily'
        )
        
        if df_ts is not None and not df_ts.empty:
            print(f"時系列データ取得成功: {len(df_ts)}日分")
            print(df_ts.tail(5))
            
            # 利回りの妥当性チェック（通常1-10%程度）
            latest_yield = df_ts['CLOSE'].iloc[-1] if 'CLOSE' in df_ts.columns else None
            if latest_yield and 0.5 <= latest_yield <= 15:
                print(f"✅ 利回り水準が妥当: {latest_yield:.4f}%")
            else:
                print(f"⚠️  利回り水準要確認: {latest_yield}")
        else:
            print("時系列データ取得失敗")
            
    except Exception as e:
        print(f"時系列データエラー: {e}")

print("\n=== テスト完了 ===")