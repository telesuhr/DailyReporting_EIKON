#!/usr/bin/env python3
"""
LMEトレーディング向け重要指標データ検証
需要・供給・マージン・コスト指標の包括的テスト
"""

import eikon as ek
import json
import warnings
from datetime import datetime, timedelta
import pandas as pd

warnings.filterwarnings('ignore')

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ek.set_app_key(config['eikon_api_key'])

print("=== LMEトレーディング重要指標検証 ===")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 検証対象RIC候補（優先度順）
critical_indicators = {
    # 1. 需要サイド指標
    "DEMAND_INDICATORS": {
        # 中国電力・ケーブル
        "CHINA-CABLE-PROD": "中国電力ケーブル生産量",
        "CN-CABLE-OUTPUT": "中国ケーブル生産統計",
        "CHINA-WIRE-PROD": "中国電線生産量",
        "CN-POWER-CABLE": "中国電力ケーブル需要",
        "CABLE-PROD-CN": "ケーブル生産中国",
        
        # 中国空調・家電
        "CHINA-AC-PROD": "中国空調生産台数",
        "CN-AIRCOND-OUTPUT": "中国エアコン生産",
        "CHINA-HVAC-PROD": "中国HVAC生産統計",
        
        # 中国不動産
        "CHINA-PROP-START": "中国不動産着工面積",
        "CN-HOUSING-START": "中国住宅着工統計",
        "CHINA-CONSTRUCTION": "中国建設統計",
        "CNCRHI=ECI": "中国不動産投資",
        
        # 自動車・EV
        "CHINA-AUTO-PROD": "中国自動車生産",
        "CN-EV-PRODUCTION": "中国EV生産台数",
        "CHINA-NEV-OUTPUT": "中国新エネ車生産"
    },
    
    # 2. TC/RC・マージン指標  
    "MARGIN_INDICATORS": {
        # TC/RC料金
        "COPPER-TCRC": "銅TC/RC料金",
        "CU-TC-RC": "銅処理精錬料金",
        "TC-RC-BENCHMARK": "TC/RCベンチマーク",
        "SHANGHAI-TCRC": "上海TC/RC",
        "SMM-CU-TCRC": "SMM銅TC/RC",
        "TCRC-SPOT-CN": "中国TC/RCスポット",
        
        # 精鉱プレミアム
        "CU-CONCENTRATE": "銅精鉱価格",
        "COPPER-CONC-PREMIUM": "銅精鉱プレミアム",
        
        # 硫酸価格（副産物）
        "SULFURIC-ACID-CN": "中国硫酸価格",
        "H2SO4-PRICE-CN": "硫酸価格中国"
    },
    
    # 3. エネルギー・コスト指標
    "COST_INDICATORS": {
        # 電力価格
        "CHILE-ELECTRICITY": "チリ電力価格",
        "CHILE-POWER-COST": "チリ電力コスト", 
        "CL-ELECTRICITY": "チリ電気料金",
        
        # 燃料価格
        "DIESEL-CHILE": "チリディーゼル価格",
        "CHILE-FUEL-COST": "チリ燃料コスト",
        
        # 中国電力
        "CHINA-POWER-PRICE": "中国電力価格",
        "CN-ELECTRICITY": "中国電気料金"
    },
    
    # 4. スクラップ・リサイクル
    "SCRAP_INDICATORS": {
        # スクラップ価格
        "COPPER-SCRAP-CN": "中国銅スクラップ価格",
        "CU-SCRAP-PRICE": "銅スクラップ価格",
        "SCRAP-CU-SHANGHAI": "上海銅スクラップ",
        "SMM-CU-SCRAP": "SMM銅スクラップ",
        
        # スクラップ比率
        "SCRAP-RATIO-CN": "中国スクラップ使用率",
        "CU-SCRAP-SPREAD": "新地金・スクラップスプレッド"
    },
    
    # 5. 金融・投機指標
    "FINANCIAL_INDICATORS": {
        # 建玉推移
        "LME-CU-OI": "LME銅建玉",
        "SHFE-CU-OI": "上海銅建玉",
        
        # ETF資金フロー
        "COPPER-ETF-FLOW": "銅ETF資金フロー",
        "JJC-FLOW": "JJC ETFフロー",
        
        # 現物プレミアム
        "CU-PHYSICAL-PREMIUM": "銅現物プレミアム",
        "REGIONAL-PREMIUM-CU": "地域別銅プレミアム"
    }
}

def test_indicator(ric, description):
    """指標データ取得テスト"""
    try:
        # 静的データテスト
        fields = ['CF_LAST', 'CF_CLOSE', 'CF_DATE', 'VALUE', 'PCTCHNG']
        df, err = ek.get_data(ric, fields)
        
        if err:
            return {'status': 'error', 'message': str(err)}
        
        if df is not None and not df.empty:
            # 有効なデータ確認
            for field in ['CF_LAST', 'CF_CLOSE', 'VALUE']:
                if field in df.columns:
                    value = df[field].iloc[0]
                    if value is not None and str(value) != 'nan' and str(value) != '<NA>':
                        date_val = df['CF_DATE'].iloc[0] if 'CF_DATE' in df.columns else 'N/A'
                        return {
                            'status': 'success',
                            'value': value,
                            'date': date_val,
                            'field': field
                        }
            
            return {'status': 'no_data', 'message': 'データなし'}
        else:
            return {'status': 'invalid', 'message': 'RIC無効'}
            
    except Exception as e:
        return {'status': 'exception', 'message': str(e)}

def test_timeseries(ric):
    """時系列データテスト（簡易版）"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        ts_data = ek.get_timeseries(
            rics=[ric],
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            interval='daily'
        )
        
        if ts_data is not None and not ts_data.empty:
            return {
                'available': True,
                'points': len(ts_data),
                'latest': ts_data.index[-1].strftime('%Y-%m-%d')
            }
        else:
            return {'available': False}
            
    except:
        return {'available': False}

# 各カテゴリーをテスト
successful_indicators = []
partial_indicators = []

for category, indicators in critical_indicators.items():
    print(f"\n=== {category} ===")
    category_success = []
    
    for ric, description in indicators.items():
        result = test_indicator(ric, description)
        
        if result['status'] == 'success':
            print(f"✅ {ric}: {description}")
            print(f"   値: {result['value']}, 日付: {result['date']}")
            
            # 時系列もチェック
            ts_result = test_timeseries(ric)
            if ts_result['available']:
                print(f"   時系列: {ts_result['points']}ポイント")
            
            successful_indicators.append({
                'ric': ric,
                'description': description,
                'category': category,
                'value': result['value'],
                'date': result['date']
            })
            
        elif result['status'] == 'no_data':
            print(f"○ {ric}: RIC有効だがデータなし")
            partial_indicators.append((ric, description))
            
        else:
            print(f"❌ {ric}: {result.get('message', 'エラー')}")

# 結果サマリー
print(f"\n=== 検証結果サマリー ===")
print(f"✅ 成功: {len(successful_indicators)}個")
print(f"○ 部分的: {len(partial_indicators)}個")

if successful_indicators:
    print(f"\n🎯 実装可能な重要指標:")
    for indicator in successful_indicators:
        print(f"  {indicator['category']}:")
        print(f"    - {indicator['ric']}: {indicator['description']}")
        print(f"      最新値: {indicator['value']} ({indicator['date']})")

# 代替アプローチ提案
print(f"\n💡 代替アプローチ提案:")
print("【需要指標の代替】")
print("- 中国PMI・工業生産（実装済み）で間接把握")
print("- 主要銅消費企業の株価（家電・自動車）")
print("- 中国電力消費統計（銅需要相関）")

print("\n【TC/RCの代替】") 
print("- 精錬会社の利益率（上場企業決算）")
print("- 銅精鉱輸入量vs精錬銅生産量")
print("- 主要精錬所の稼働率")

print("\n【コスト指標の代替】")
print("- エネルギー関連ETF・原油価格")
print("- 南米通貨（チリペソ・ペルーソル）")
print("- 鉱山会社の開示コストデータ")

print(f"\n=== テスト完了 ===")