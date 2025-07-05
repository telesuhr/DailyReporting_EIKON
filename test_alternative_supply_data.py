#!/usr/bin/env python3
"""
代替サプライチェーンデータ検証
経済統計・企業データ・代替指標での取得テスト
"""

import eikon as ek
import json
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ek.set_app_key(config['eikon_api_key'])

print("=== 代替サプライチェーンデータ検証 ===")

# より現実的なRIC候補
alternative_supply_rics = {
    # 経済統計系（政府発表データ）
    "ECONOMIC_STATISTICS": {
        "CHILE.IP": "チリ工業生産指数",
        "CHILE.MINING": "チリ鉱業指数", 
        "PERU.IP": "ペルー工業生産",
        "CHINA.MINING": "中国鉱業指数",
        "WORLD.METALS.PROD": "世界金属生産",
        "GLOBAL.MINING.INDEX": "世界鉱業指数"
    },
    
    # 主要企業株価・ファンダメンタルズ（間接指標）
    "MINING_COMPANIES": {
        "FCX.N": "Freeport-McMoRan株価",
        "VALE.N": "Vale株価",
        "BHP.AX": "BHP株価",
        "RIO.L": "Rio Tinto株価",
        "GLEN.L": "Glencore株価",
        "ANTO.L": "Antofagasta株価",
        "SCCO.N": "Southern Copper株価"
    },
    
    # セクター・ETF指標
    "SECTOR_INDICES": {
        "XME": "SPDR Metals & Mining ETF",
        "PICK": "iShares MSCI Global Metals & Mining ETF",
        "COPX": "Global X Copper Miners ETF",
        "GDXJ": "Junior Gold Miners ETF",
        ".SPMETAL": "S&P Metals & Mining Index"
    },
    
    # コモディティ指数・関連指標
    "COMMODITY_INDICES": {
        "CRB": "CRB Index",
        "DJP": "DJP Commodity ETF",
        "GSCI": "Goldman Sachs Commodity Index",
        "RICI": "Rogers International Commodity Index"
    },
    
    # エネルギー・電力コスト（生産コスト代理）
    "ENERGY_COSTS": {
        "TTF": "TTF Natural Gas",
        "COAL": "Coal Index",
        "ELECTRICITY.CHILE": "チリ電力価格",
        "POWER.CHINA": "中国電力指数"
    },
    
    # 貿易・輸送指標
    "TRADE_TRANSPORT": {
        "BALTIC": "Baltic Dry Index",
        "HARPEX": "Harper Petersen Index",
        "CCFI": "China Containerized Freight Index",
        "BDIY": "Baltic Dry Index"
    },
    
    # 代替的生産指標
    "PROXY_PRODUCTION": {
        "ICSG.CU.PROD": "ICSG銅生産統計",
        "LME.CU.PRODUCTION": "LME生産データ",
        "WBMS.CU": "WBMS銅統計",
        "ANTAIKE.CU": "Antaike銅統計"
    }
}

def enhanced_ric_test(ric, description):
    """拡張RICテスト"""
    try:
        # より多くのフィールドでテスト
        fields = ['CF_LAST', 'CF_CLOSE', 'CF_OPEN', 'CF_HIGH', 'CF_LOW', 
                 'CF_VOLUME', 'CF_DATE', 'PCTCHNG', 'VALUE']
        df, err = ek.get_data(ric, fields)
        
        result = {
            'ric': ric,
            'description': description,
            'status': 'unknown',
            'data_quality': 'none',
            'latest_value': None,
            'data_date': None,
            'available_fields': [],
            'errors': []
        }
        
        if err:
            result['errors'] = [str(err)]
        
        if df is not None and not df.empty:
            result['status'] = 'accessible'
            
            # 利用可能フィールドを特定
            for field in fields:
                if field in df.columns:
                    value = df[field].iloc[0]
                    if value is not None and str(value) != 'nan' and str(value) != '<NA>':
                        result['available_fields'].append(field)
                        if result['latest_value'] is None:
                            result['latest_value'] = value
            
            if result['available_fields']:
                result['data_quality'] = 'good'
                
            if 'CF_DATE' in df.columns:
                result['data_date'] = df['CF_DATE'].iloc[0]
        
        return result
        
    except Exception as e:
        return {
            'ric': ric,
            'description': description, 
            'status': 'error',
            'data_quality': 'none',
            'latest_value': None,
            'data_date': None,
            'available_fields': [],
            'errors': [str(e)]
        }

# テスト実行
successful_data = []
partially_successful = []

for category, rics in alternative_supply_rics.items():
    print(f"\n=== {category} ===")
    
    for ric, description in rics.items():
        print(f"\n--- {ric} ({description}) ---")
        
        result = enhanced_ric_test(ric, description)
        
        if result['data_quality'] == 'good':
            print(f"  ✅ 高品質データ: {result['latest_value']} ({result['data_date']})")
            print(f"     利用可能フィールド: {', '.join(result['available_fields'])}")
            successful_data.append(result)
            
        elif result['status'] == 'accessible':
            print(f"  ○ アクセス可能（データ限定）")
            print(f"     利用可能フィールド: {', '.join(result['available_fields'])}")
            partially_successful.append(result)
            
        else:
            print(f"  ❌ アクセス不可: {result['errors']}")

# 結果サマリー
print(f"\n=== 代替データ検証結果 ===")
print(f"✅ 高品質データ: {len(successful_data)}個")
print(f"○ 部分的データ: {len(partially_successful)}個")

if successful_data:
    print(f"\n📊 実装可能な代替指標:")
    for result in successful_data:
        print(f"  - {result['ric']}: {result['description']}")
        print(f"    値: {result['latest_value']}, 日付: {result['data_date']}")

if partially_successful:
    print(f"\n⚠️  制限付きアクセス可能:")
    for result in partially_successful:
        print(f"  - {result['ric']}: {result['description']}")

# Workspace検索のための具体的推奨
print(f"\n🔍 Workspace検索推奨（具体的キーワード）:")
print("【生産統計】")
print("- copper production statistics")
print("- mine production data") 
print("- smelter capacity utilization")
print("- Chile copper output")
print("- Peru mining production")
print("- China refined copper")

print("\n【企業決算データ】")
print("- Freeport production guidance")
print("- BHP copper production")
print("- Vale base metals")
print("- Glencore copper segment")

print("\n【業界統計】")
print("- ICSG copper statistics")
print("- WBMS copper data")
print("- CRU copper intelligence")
print("- Wood Mackenzie copper")

print("\n【処理料金・マージン】")
print("- copper TC RC benchmark")
print("- smelter treatment charge")
print("- copper concentrate price")

print(f"\n=== テスト完了 ===")
print("有効なデータが見つかった場合は、間接的サプライチェーン指標として活用可能です。")