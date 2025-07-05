#!/usr/bin/env python3
"""
中国工業生産指数 CNIO系RICのテスト
CNIO=ECI, CNIPY=ECI, CNIO=ECIX
"""

import eikon as ek
import json
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ek.set_app_key(config['eikon_api_key'])

# テスト対象RIC
test_rics = {
    'CNIO=ECI': '中国工業生産指数（CNIO形式）',
    'CNIPY=ECI': '中国工業生産指数（既存設定）',
    'CNIO=ECIX': '中国工業生産指数（ECIX形式）'
}

print("=== CNIO系RIC包括テスト ===")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

successful_rics = []

for ric, description in test_rics.items():
    print(f"\n--- {ric} ({description}) ---")
    
    try:
        # 複数フィールドで取得テスト
        fields = ['CF_LAST', 'CF_CLOSE', 'CF_DATE', 'PCTCHNG']
        df, err = ek.get_data(ric, fields)
        
        if err:
            print(f"  警告: {err}")
        
        if df is not None and not df.empty:
            has_valid_data = False
            print("  📊 取得データ:")
            
            for col in df.columns:
                if col != 'Instrument':
                    value = df[col].iloc[0]
                    if value is not None and str(value) != 'nan' and str(value) != '<NA>':
                        print(f"    {col}: {value}")
                        has_valid_data = True
                    else:
                        print(f"    {col}: <データなし>")
            
            if has_valid_data:
                successful_rics.append((ric, description))
                
                # 数値の妥当性チェック（工業生産指数は通常-20%〜+30%）
                value = None
                if 'CF_LAST' in df.columns:
                    value = df['CF_LAST'].iloc[0]
                elif 'CF_CLOSE' in df.columns:
                    value = df['CF_CLOSE'].iloc[0]
                
                if value is not None and str(value) != 'nan' and str(value) != '<NA>':
                    try:
                        num_value = float(value)
                        if -30 <= num_value <= 50:
                            print(f"    ✅ 値が妥当範囲内: {num_value}")
                        else:
                            print(f"    ⚠️  値要確認: {num_value}")
                    except:
                        print(f"    ⚠️  数値変換不可: {value}")
                
                # 時系列データテスト
                print(f"  📈 時系列データテスト:")
                try:
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=60)
                    
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
                            print(f"    最新値: {latest}")
                    else:
                        print(f"    ⚠️  時系列データなし")
                        
                except Exception as ts_e:
                    print(f"    ❌ 時系列エラー: {ts_e}")
                    
            else:
                print(f"    ○ RIC有効だが有効データなし")
        else:
            print(f"    ❌ レスポンスなし")
            
    except Exception as e:
        print(f"    ❌ エラー: {e}")

# 結果サマリー
print(f"\n=== 結果サマリー ===")
if successful_rics:
    print("✅ 使用可能なRIC:")
    for ric, desc in successful_rics:
        print(f"  - {ric}: {desc}")
    
    # 推奨RIC
    if len(successful_rics) > 0:
        best_ric = successful_rics[0][0]
        print(f"\n🎯 推奨RIC: {best_ric}")
        print("config.jsonの更新推奨:")
        print(f'    "CHINA_IND_PROD": "{best_ric}"')
else:
    print("❌ 有効なRICが見つかりませんでした")

print(f"\n=== テスト完了 ===")