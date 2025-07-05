#!/usr/bin/env python3
"""
実用的な代替指標検証
EIKONで実際に取得可能な指標による代替アプローチ
"""

import eikon as ek
import json
import warnings
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ek.set_app_key(config['eikon_api_key'])

print("=== 実用的代替指標検証 ===")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 実用的な代替指標（取得可能性が高い）
practical_alternatives = {
    # 1. 需要代理指標
    "DEMAND_PROXIES": {
        # 中国経済活動
        "CNCPIELEC=ECI": "中国電力消費指数",
        "CNELCTY=ECI": "中国電力生産",
        "CNELCONSYY=ECI": "中国電力消費前年比",
        
        # 銅消費関連企業株価
        "600690.SS": "青島海爾（Haier・家電大手）",
        "000333.SZ": "美的集団（Midea・空調大手）",
        "002594.SZ": "BYD（電気自動車）",
        "600104.SS": "上海汽車（SAIC Motor）",
        
        # 不動産・建設
        "CNHPIYY=ECI": "中国住宅価格指数",
        "CNFAI=ECI": "中国固定資産投資"
    },
    
    # 2. コスト・通貨指標
    "COST_PROXIES": {
        # 南米通貨（生産コスト代理）
        "CLP=": "チリペソ/USD",
        "PEN=": "ペルーソル/USD",
        "COP=": "コロンビアペソ/USD",
        
        # エネルギー価格
        "NYMRB1": "RBOB ガソリン先物",
        "HOILF1": "暖房油先物",
        "NG1": "天然ガス先物（既存）"
    },
    
    # 3. 銅関連ETF・投資商品
    "COPPER_INVESTMENT": {
        "JJC": "iPath Bloomberg Copper ETN",
        "CPER": "United States Copper Index Fund",
        "COPX": "Global X Copper Miners ETF",
        "JJCTF": "iPath Series B Bloomberg Copper ETN"
    },
    
    # 4. 精錬・加工企業
    "SMELTER_COMPANIES": {
        "601600.SS": "中国アルミ（精錬大手）",
        "600362.SS": "江西銅業（Jiangxi Copper）",
        "000878.SZ": "雲南銅業（Yunnan Copper）",
        "600459.SS": "貴研鉄金属（精錬技術）"
    },
    
    # 5. 建玉・ボラティリティ
    "MARKET_STRUCTURE": {
        # LME関連
        "0#LME-CU:": "LME銅チェーン",
        "LME-CMCU3": "LME銅3ヶ月詳細",
        
        # ボラティリティ
        "CMCU3IV1M=": "LME銅1ヶ月インプライドボラティリティ",
        "CMCU3HV30=": "LME銅30日ヒストリカルボラティリティ"
    },
    
    # 6. 地域プレミアム・ベーシス
    "REGIONAL_BASIS": {
        # 既存の上海プレミアム拡張
        "SHFE-LME-CU": "上海/LME銅ベーシス",
        "COMEX-LME-CU": "COMEX/LME銅ベーシス",
        
        # 為替調整後スプレッド
        "CNY=": "USD/CNY（既存）",
        "JPYUSD=": "JPY/USD"
    }
}

def test_with_details(ric, description):
    """詳細テスト"""
    try:
        # 静的データ
        fields = ['CF_LAST', 'CF_CLOSE', 'CF_DATE', 'PCTCHNG', 'CF_VOLUME']
        df, err = ek.get_data(ric, fields)
        
        if df is not None and not df.empty:
            result = {'success': True, 'data': {}}
            
            for field in fields:
                if field in df.columns:
                    value = df[field].iloc[0]
                    if value is not None and str(value) != 'nan' and str(value) != '<NA>':
                        result['data'][field] = value
            
            if result['data']:
                return result
        
        return {'success': False}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

# テスト実行
successful_alternatives = []

for category, indicators in practical_alternatives.items():
    print(f"\n=== {category} ===")
    
    for ric, description in indicators.items():
        result = test_with_details(ric, description)
        
        if result['success'] and result.get('data'):
            print(f"✅ {ric}: {description}")
            if 'CF_LAST' in result['data']:
                print(f"   最新値: {result['data']['CF_LAST']}")
            if 'CF_DATE' in result['data']:
                print(f"   日付: {result['data']['CF_DATE']}")
            if 'PCTCHNG' in result['data']:
                print(f"   変化率: {result['data']['PCTCHNG']}%")
                
            successful_alternatives.append({
                'category': category,
                'ric': ric,
                'description': description,
                'data': result['data']
            })
        else:
            print(f"❌ {ric}: 取得失敗")

# 実装推奨
print(f"\n=== 実装推奨代替指標 ===")
print(f"✅ 成功: {len(successful_alternatives)}個")

if successful_alternatives:
    # カテゴリ別集計
    by_category = {}
    for item in successful_alternatives:
        cat = item['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)
    
    print(f"\n🎯 カテゴリ別実装推奨:")
    for cat, items in by_category.items():
        print(f"\n【{cat}】({len(items)}個)")
        for item in items:
            print(f"  - {item['ric']}: {item['description']}")
            if 'CF_LAST' in item['data']:
                print(f"    値: {item['data']['CF_LAST']}")

# 統合戦略提案
print(f"\n💡 統合分析戦略:")
print("1. 【需要分析】")
print("   - 中国電力消費 → 銅需要の先行指標")
print("   - 家電・自動車株 → 最終需要の健全性")
print("   - 固定資産投資 → インフラ需要")

print("\n2. 【コスト分析】")
print("   - 南米通貨 → 生産コストの代理指標")
print("   - エネルギー価格 → 操業コスト")
print("   - 鉱山会社株価 → 総合的収益性")

print("\n3. 【市場構造分析】")  
print("   - 銅ETF資金フロー → 投資需要")
print("   - ボラティリティ → 市場不確実性")
print("   - 地域間スプレッド → 裁定機会")

print(f"\n=== テスト完了 ===")