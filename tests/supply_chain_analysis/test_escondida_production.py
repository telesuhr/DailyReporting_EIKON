#!/usr/bin/env python3
"""
Escondida鉱山生産データ検証
世界最大銅鉱山の月次生産統計テスト
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

print("=== Escondida鉱山生産データ検証 ===")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Escondida関連RIC候補
escondida_rics = {
    "CCOCUPRDESH": "Escondida Monthly Copper Production (あなた発見)",
    "ESCONDIDA-PROD": "Escondida Production (一般的)",
    "ESC-CU-PROD": "Escondida Copper Production",
    "BHP-ESC-PROD": "BHP Escondida Production",
    "ESCONDIDA.CU": "Escondida Copper Output"
}

def comprehensive_ric_test(ric, description):
    """包括的RICテスト（静的データ＋時系列）"""
    try:
        result = {
            'ric': ric,
            'description': description,
            'static_data': None,
            'timeseries_data': None,
            'success': False,
            'data_type': 'none',
            'latest_value': None,
            'data_date': None,
            'data_frequency': 'unknown',
            'errors': []
        }
        
        # 1. 静的データテスト
        print(f"  📊 静的データテスト...")
        fields = ['CF_LAST', 'CF_CLOSE', 'CF_DATE', 'VALUE', 'CF_VOLUME']
        try:
            df, err = ek.get_data(ric, fields)
            if err:
                result['errors'].append(f"静的データエラー: {err}")
            
            if df is not None and not df.empty:
                result['static_data'] = 'available'
                for field in ['CF_LAST', 'CF_CLOSE', 'VALUE']:
                    if field in df.columns:
                        value = df[field].iloc[0]
                        if value is not None and str(value) != 'nan':
                            result['latest_value'] = value
                            result['success'] = True
                            result['data_type'] = 'static'
                            break
                
                if 'CF_DATE' in df.columns:
                    result['data_date'] = df['CF_DATE'].iloc[0]
                    
                print(f"    ✅ 静的データ取得: {result['latest_value']} ({result['data_date']})")
            else:
                print(f"    ❌ 静的データなし")
                
        except Exception as e:
            result['errors'].append(f"静的データ例外: {str(e)}")
            print(f"    ⚠️  静的データ例外: {e}")
        
        # 2. 時系列データテスト（過去2年）
        print(f"  📈 時系列データテスト...")
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)  # 2年分
            
            ts_data = ek.get_timeseries(
                rics=[ric],
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                interval='monthly'  # 月次データに最適化
            )
            
            if ts_data is not None and not ts_data.empty:
                result['timeseries_data'] = 'available'
                result['success'] = True
                result['data_type'] = 'timeseries'
                
                # データ品質分析
                data_points = len(ts_data)
                date_range = f"{ts_data.index.min().strftime('%Y-%m')} to {ts_data.index.max().strftime('%Y-%m')}"
                
                # 最新値取得
                if 'CLOSE' in ts_data.columns:
                    latest_ts_value = ts_data['CLOSE'].iloc[-1]
                    latest_ts_date = ts_data.index[-1]
                    
                    if result['latest_value'] is None:
                        result['latest_value'] = latest_ts_value
                        result['data_date'] = latest_ts_date
                
                # 月次頻度判定
                if data_points >= 12:  # 1年以上
                    result['data_frequency'] = 'monthly'
                elif data_points >= 4:  # 四半期以上
                    result['data_frequency'] = 'quarterly'
                else:
                    result['data_frequency'] = 'sparse'
                
                print(f"    ✅ 時系列データ: {data_points}ポイント")
                print(f"       期間: {date_range}")
                print(f"       最新値: {result['latest_value']} ({result['data_date']})")
                
                # 実際の生産レベル判定（合理性チェック）
                if result['latest_value'] and isinstance(result['latest_value'], (int, float)):
                    production_level = result['latest_value']
                    if 50000 <= production_level <= 200000:  # 月次50-200kt範囲
                        print(f"    🎯 生産量レベル: 合理的 ({production_level:,.0f}トン/月)")
                    elif 50 <= production_level <= 200:  # kt単位かもしれない
                        print(f"    🎯 生産量レベル: kt単位の可能性 ({production_level}kt/月)")
                    else:
                        print(f"    ⚠️  生産量レベル: 要確認 ({production_level})")
                
            else:
                print(f"    ❌ 時系列データなし")
                
        except Exception as e:
            result['errors'].append(f"時系列データ例外: {str(e)}")
            print(f"    ⚠️  時系列データ例外: {e}")
        
        return result
        
    except Exception as e:
        return {
            'ric': ric,
            'description': description,
            'static_data': None,
            'timeseries_data': None,
            'success': False,
            'data_type': 'error',
            'latest_value': None,
            'data_date': None,
            'data_frequency': 'unknown',
            'errors': [str(e)]
        }

# 各RICを包括テスト
successful_results = []

for ric, description in escondida_rics.items():
    print(f"\n=== {ric} ({description}) ===")
    
    result = comprehensive_ric_test(ric, description)
    
    if result['success']:
        successful_results.append(result)
        print(f"✅ 成功: {result['data_type']}データで {result['latest_value']}")
    else:
        print(f"❌ 失敗: {', '.join(result['errors'])}")

# 結果サマリー
print(f"\n=== Escondida検証結果サマリー ===")
print(f"✅ 成功RIC: {len(successful_results)}個")

if successful_results:
    print(f"\n📊 利用可能なEscondida生産データ:")
    for result in successful_results:
        print(f"  - {result['ric']}: {result['description']}")
        print(f"    値: {result['latest_value']}, 日付: {result['data_date']}")
        print(f"    データ型: {result['data_type']}, 頻度: {result['data_frequency']}")
    
    # 実装推奨
    best_ric = successful_results[0]  # 最初に成功したものを推奨
    print(f"\n🔧 実装推奨設定:")
    print(f"\"escondida_production\": {{")
    print(f"  \"ric\": \"{best_ric['ric']}\",")
    print(f"  \"name\": \"{best_ric['description']}\",")
    print(f"  \"note\": \"世界最大銅鉱山・月次生産統計({best_ric['data_frequency']})\",")
    print(f"  \"latest_value\": {best_ric['latest_value']},")
    print(f"  \"data_date\": \"{best_ric['data_date']}\",")
    print(f"  \"significance\": \"全世界銅生産の約5%を占める最重要指標\"")
    print(f"}}")
    
else:
    print(f"\n❌ Escondida生産データは取得できませんでした")

# Escondidaの重要性説明
print(f"\n🌟 Escondida鉱山の戦略的重要性:")
print("- 世界最大の銅鉱山（年産約100万トン）")
print("- 全世界銅生産の約5%を占める")
print("- BHP Billiton運営（57.5%権益）")
print("- チリ・アタカマ砂漠に位置")
print("- 生産変動が全世界の銅需給に直接影響")
print("- ストライキ・設備トラブル時の市場インパクト甚大")

print(f"\n💡 ディレイについて:")
print("- 月次データは通常1-2ヶ月のディレイ")
print("- しかし生産トレンド・季節性分析には十分有効")
print("- ストライキ・メンテナンス計画の影響分析に重要")
print("- 中長期的なサプライ見通しの基礎データ")

print(f"\n=== テスト完了 ===")