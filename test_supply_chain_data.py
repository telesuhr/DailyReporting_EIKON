#!/usr/bin/env python3
"""
サプライチェーン・生産データ取得可能性検証
EIKON Data APIでの鉱山生産・精錬データ取得テスト
"""

import eikon as ek
import json
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ek.set_app_key(config['eikon_api_key'])

print("=== サプライチェーン・生産データ検証 ===")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 検証対象RIC候補
supply_chain_rics = {
    # 世界的鉱山生産データ
    "GLOBAL_PRODUCTION": {
        "WORLD-CU-MINE": "世界銅鉱山生産量",
        "WORLD-CU-PROD": "世界銅生産量",
        "GLOBAL-CU-OUTPUT": "グローバル銅産出量",
        "CU-MINE-PROD": "銅鉱山生産データ",
        "COPPER-MINE-GLOBAL": "銅鉱山グローバル",
        "MINE-CU-TOTAL": "鉱山銅合計"
    },
    
    # 地域別生産データ
    "REGIONAL_PRODUCTION": {
        "CHILE-CU-PROD": "チリ銅生産",
        "PERU-CU-PROD": "ペルー銅生産", 
        "CHINA-CU-PROD": "中国銅生産",
        "US-CU-PROD": "米国銅生産",
        "AUSTRALIA-CU-PROD": "豪州銅生産",
        "ZAMBIA-CU-PROD": "ザンビア銅生産"
    },
    
    # 精錬・製錬データ
    "SMELTING_REFINING": {
        "CU-SMELTER-PROD": "銅製錬生産",
        "CU-REFINERY-PROD": "銅精錬生産",
        "TC-RC-CU": "銅TC/RC料金",
        "CU-TREATMENT-CHARGE": "銅処理料金",
        "SMELTER-CU-CAP": "製錬所銅能力",
        "REFINERY-CU-UTIL": "精錬所稼働率"
    },
    
    # 主要鉱山会社
    "MAJOR_MINERS": {
        "VALE-CU-PROD": "Vale銅生産",
        "BHP-CU-PROD": "BHP銅生産", 
        "RIO-CU-PROD": "Rio Tinto銅生産",
        "GLENCORE-CU-PROD": "Glencore銅生産",
        "FCX-CU-PROD": "Freeport銅生産",
        "ANTOFAGASTA-CU-PROD": "Antofagasta銅生産"
    },
    
    # 鉱山特定データ
    "SPECIFIC_MINES": {
        "ESCONDIDA-PROD": "Escondida鉱山",
        "GRASBERG-PROD": "Grasberg鉱山",
        "MORENCI-PROD": "Morenci鉱山",
        "COLLAHUASI-PROD": "Collahuasi鉱山",
        "CERRO-VERDE-PROD": "Cerro Verde鉱山"
    },
    
    # 容量・稼働率
    "CAPACITY_UTILIZATION": {
        "CU-MINE-CAP": "銅鉱山キャパシティ",
        "CU-MINE-UTIL": "銅鉱山稼働率",
        "CU-SMELT-UTIL": "銅製錬稼働率",
        "MINE-UTIL-GLOBAL": "世界鉱山稼働率"
    }
}

def test_ric_data(ric, description):
    """個別RICのデータ取得テスト"""
    try:
        # 基本フィールドでテスト
        fields = ['CF_LAST', 'CF_CLOSE', 'CF_DATE', 'VALUE']
        df, err = ek.get_data(ric, fields)
        
        result = {
            'ric': ric,
            'description': description,
            'success': False,
            'data_found': False,
            'latest_value': None,
            'data_date': None,
            'errors': []
        }
        
        if err:
            result['errors'].append(str(err))
        
        if df is not None and not df.empty:
            result['success'] = True
            
            # 有効なデータがあるかチェック
            for field in ['CF_LAST', 'CF_CLOSE', 'VALUE']:
                if field in df.columns:
                    value = df[field].iloc[0]
                    if value is not None and str(value) != 'nan' and str(value) != '<NA>':
                        result['data_found'] = True
                        result['latest_value'] = value
                        break
            
            if 'CF_DATE' in df.columns:
                result['data_date'] = df['CF_DATE'].iloc[0]
        
        return result
        
    except Exception as e:
        return {
            'ric': ric,
            'description': description,
            'success': False,
            'data_found': False,
            'latest_value': None,
            'data_date': None,
            'errors': [str(e)]
        }

def test_timeseries_data(ric, description):
    """時系列データ取得テスト"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)  # 1年分
        
        ts_data = ek.get_timeseries(
            rics=[ric],
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            interval='daily'
        )
        
        if ts_data is not None and not ts_data.empty:
            return {
                'timeseries_success': True,
                'data_points': len(ts_data),
                'date_range': f"{ts_data.index.min()} to {ts_data.index.max()}",
                'latest_value': ts_data['CLOSE'].iloc[-1] if 'CLOSE' in ts_data.columns else None
            }
        else:
            return {'timeseries_success': False}
            
    except Exception as e:
        return {'timeseries_success': False, 'timeseries_error': str(e)}

# 各カテゴリーをテスト
all_results = {}
successful_rics = []

for category, rics in supply_chain_rics.items():
    print(f"\n=== {category} ===")
    category_results = []
    
    for ric, description in rics.items():
        print(f"\n--- {ric} ({description}) ---")
        
        # 基本データテスト
        result = test_ric_data(ric, description)
        
        if result['success']:
            if result['data_found']:
                print(f"  ✅ データ取得成功: {result['latest_value']} ({result['data_date']})")
                successful_rics.append((ric, description, result['latest_value']))
                
                # 時系列データもテスト
                ts_result = test_timeseries_data(ric, description)
                result.update(ts_result)
                
                if ts_result.get('timeseries_success'):
                    print(f"  📈 時系列データ: {ts_result['data_points']}ポイント")
                    print(f"     期間: {ts_result['date_range']}")
                else:
                    print(f"  ⚠️  時系列データなし")
            else:
                print(f"  ○ RIC有効だがデータなし")
        else:
            print(f"  ❌ RIC無効: {result['errors']}")
        
        category_results.append(result)
    
    all_results[category] = category_results

# 結果サマリー
print(f"\n=== 総合結果サマリー ===")
print(f"✅ データ取得成功RIC: {len(successful_rics)}個")

if successful_rics:
    print(f"\n📊 成功したサプライチェーンデータ:")
    for ric, desc, value in successful_rics:
        print(f"  - {ric}: {desc} (値: {value})")
    
    print(f"\n🔧 実装推奨RIC設定:")
    print("supply_chain_rics = {")
    for ric, desc, value in successful_rics:
        print(f'    "{ric}": "{desc}",  # 値: {value}')
    print("}")
    
else:
    print(f"\n❌ 利用可能なサプライチェーンデータが見つかりませんでした")

# Workspaceでの検索推奨キーワード
print(f"\n🔍 Workspace検索推奨キーワード:")
print("【鉱山生産】")
print("- copper mine production")
print("- mining output")
print("- smelter production") 
print("- refinery capacity")

print("\n【地域別】")
print("- Chile copper")
print("- Peru copper")
print("- China copper production")

print("\n【企業別】")
print("- BHP copper")
print("- Vale copper") 
print("- Freeport copper")
print("- Glencore copper")

print("\n【処理料金】")
print("- TC RC copper")
print("- treatment charge")
print("- smelting margin")

print(f"\n=== テスト完了 ===")
print("次に有効なRICが見つかった場合、config.jsonに追加して機能拡張できます。")