#!/usr/bin/env python3
"""
VIX代替RICの動作確認テスト
各種ボラティリティ指数の取得可能性をチェック
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

# テスト対象のVIX代替RIC
vix_alternatives = {
    # VIX系列
    '.VIX': 'CBOE Volatility Index (Original)',
    'VIX.S': 'S&P VIX',
    '.VIXCLS': 'VIX Close Value',
    '.VXN': 'NASDAQ-100 Volatility Index',
    '.VXD': 'Dow Jones Volatility Index',
    '.OVX': 'Crude Oil Volatility Index',
    '.GVZ': 'Gold Volatility Index',
    'CBOE-VIX': 'CBOE Direct VIX',
    '^VIX': 'Yahoo Finance Format VIX',
    
    # ユーザー提供のRIC
    '.VIXIE': 'CBOE Europe Volatility Index',
    
    # その他のボラティリティ指標
    '.EVZ': 'Euro Currency Volatility',
    '.VXEEM': 'Emerging Markets Volatility',
    '.VXEFA': 'Developed Markets (ex-US) Volatility',
    
    # クレジット関連
    'ITRAXX.MAIN': 'iTraxx Europe Main',
    'ITRAXX/MAIN': 'iTraxx Europe Main (Alternative)',
    
    # 代替的なリスク指標
    'VIX': 'VIX without dot',
    'USDVIX=R': 'Reuters VIX',
    '.VIXY': 'VIX ETF',
}

print(f"=== VIX代替RICテスト ===")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 各RICをテスト
successful_rics = []
failed_rics = []

for ric, description in vix_alternatives.items():
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
                        print(f"  {field}: {value}")
                        has_valid_data = True
                        break
            
            if has_valid_data:
                if 'PCTCHNG' in df.columns and df['PCTCHNG'].iloc[0] is not None:
                    print(f"  変化率: {df['PCTCHNG'].iloc[0]:.2f}%")
                if 'CF_DATE' in df.columns:
                    print(f"  データ日付: {df['CF_DATE'].iloc[0]}")
                
                successful_rics.append((ric, description))
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
for ric, desc in successful_rics:
    print(f"  - {ric}: {desc}")

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
        start_date = end_date - timedelta(days=5)
        
        df_ts = ek.get_timeseries(
            rics=[test_ric],
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            interval='daily'
        )
        
        if df_ts is not None and not df_ts.empty:
            print(f"時系列データ取得成功: {len(df_ts)}日分")
            print(df_ts.tail(3))
        else:
            print("時系列データ取得失敗")
            
    except Exception as e:
        print(f"時系列データエラー: {e}")

print("\n=== テスト完了 ===")