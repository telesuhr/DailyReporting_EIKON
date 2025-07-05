#!/usr/bin/env python3
"""
中国経済指標（PMI含む）の動作確認テスト
LME金属レポート用の包括的な指標セットをテスト
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

# テスト対象の中国経済指標
china_indicators = {
    # PMI指標
    'CNPMIB=ECI': '中国国家統計局 製造業PMI',
    'CNMPIS=ESI': '財新サービス業PMI',
    'CNCPMI=ECI': '中国総合PMI',
    
    # 現在エラーの指標
    'CNPMIM=ECI': '現在のPMI設定（エラー）',
    'CNCPIY=ECI': '現在のCPI設定（エラー）',
    'CNGDPY=ECI': '現在のGDP設定（エラー）',
    
    # 金属需要直結指標
    'CHIPTOT.H': '工業生産指数',
    'CHIFATOTA': '固定資産投資',
    'CHPROPRCF': '生産者物価指数',
    
    # 経済全体指標
    'CHGDP...C': 'GDP（四半期）',
    'CHRETTOTA': '小売売上',
    'CHCPANNL': '消費者物価指数',
    
    # 貿易・金融指標
    'CHVISGDSA': '貿易収支',
    'CHRESERV': '外貨準備',
}

print(f"=== 中国経済指標包括テスト ===")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 各指標をテスト
successful_indicators = []
failed_indicators = []

for ric, description in china_indicators.items():
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
            value = None
            
            for field in ['CF_LAST', 'CF_CLOSE']:
                if field in df.columns:
                    value = df[field].iloc[0]
                    if value is not None and str(value) != 'nan':
                        print(f"  {field}: {value}")
                        has_valid_data = True
                        break
            
            if has_valid_data:
                if 'PCTCHNG' in df.columns and df['PCTCHNG'].iloc[0] is not None:
                    pct_change = df['PCTCHNG'].iloc[0]
                    if str(pct_change) != 'nan':
                        print(f"  変化率: {pct_change:.2f}%")
                
                if 'CF_DATE' in df.columns:
                    print(f"  データ日付: {df['CF_DATE'].iloc[0]}")
                
                # 数値の妥当性チェック
                validity_check = ""
                if 'PMI' in description and value is not None:
                    if 40 <= value <= 70:
                        validity_check = " ✅ PMI値妥当"
                    else:
                        validity_check = " ⚠️ PMI値要確認"
                elif 'CPI' in description and value is not None:
                    if -5 <= value <= 15:
                        validity_check = " ✅ CPI値妥当"
                    else:
                        validity_check = " ⚠️ CPI値要確認"
                
                successful_indicators.append((ric, description, value))
                print(f"  ✅ 成功: データ取得可能{validity_check}")
            else:
                failed_indicators.append((ric, description, "データなし"))
                print(f"  ❌ 失敗: 有効なデータなし")
        else:
            failed_indicators.append((ric, description, "空のレスポンス"))
            print(f"  ❌ 失敗: 空のレスポンス")
            
    except Exception as e:
        failed_indicators.append((ric, description, str(e)))
        print(f"  ❌ エラー: {e}")
    
    print()

# 結果サマリー
print("\n=== 結果サマリー ===")
print(f"\n✅ 成功した指標 ({len(successful_indicators)}個):")
for ric, desc, value in successful_indicators:
    print(f"  - {ric}: {desc} (値: {value})")

print(f"\n❌ 失敗した指標 ({len(failed_indicators)}個):")
for ric, desc, reason in failed_indicators:
    print(f"  - {ric}: {desc} ({reason})")

# 推奨設定
print("\n=== 推奨config.json設定 ===")
if successful_indicators:
    print("\n推奨する設定:")
    print('"china_economic_indicators": {')
    
    # PMI優先
    pmi_found = False
    for ric, desc, value in successful_indicators:
        if 'PMI' in desc and not pmi_found:
            print(f'    "CHINA_PMI": "{ric}",  // {desc}')
            pmi_found = True
    
    # その他重要指標
    priority_indicators = [
        ('工業生産', 'CHINA_INDUSTRIAL_PRODUCTION'),
        ('固定資産投資', 'CHINA_FIXED_INVESTMENT'),
        ('生産者物価', 'CHINA_PPI'),
        ('GDP', 'CHINA_GDP'),
        ('小売売上', 'CHINA_RETAIL_SALES'),
        ('消費者物価', 'CHINA_CPI'),
        ('貿易収支', 'CHINA_TRADE_BALANCE'),
        ('外貨準備', 'CHINA_FX_RESERVES')
    ]
    
    for keyword, config_name in priority_indicators:
        for ric, desc, value in successful_indicators:
            if keyword in desc:
                print(f'    "{config_name}": "{ric}",  // {desc}')
                break
    
    print('}')

print("\n=== テスト完了 ===")