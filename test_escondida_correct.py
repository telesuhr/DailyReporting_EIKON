#!/usr/bin/env python3
"""
Escondida鉱山生産データ検証（正しいRIC）
RIC: CCOCUPRDESM
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

print("=== Escondida鉱山生産データ検証（正しいRIC） ===")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 正しいRIC
ric = "CCOCUPRDESM"
description = "Escondida Monthly Copper Production (正しいRIC)"

print(f"\n=== {ric} ({description}) ===")

# 1. 静的データテスト
print(f"📊 静的データテスト...")
fields = ['CF_LAST', 'CF_CLOSE', 'CF_DATE', 'VALUE', 'CF_VOLUME', 'CF_HIGH', 'CF_LOW']
try:
    df, err = ek.get_data(ric, fields)
    
    if err:
        print(f"  ⚠️  エラー: {err}")
    
    if df is not None and not df.empty:
        print(f"  ✅ 静的データ取得成功")
        print(f"     カラム: {list(df.columns)}")
        
        for col in df.columns:
            value = df[col].iloc[0]
            print(f"     {col}: {value}")
            
    else:
        print(f"  ❌ 静的データなし")
        
except Exception as e:
    print(f"  ⚠️  静的データ例外: {e}")

# 2. 時系列データテスト（過去2年、月次）
print(f"\n📈 時系列データテスト（月次、過去2年）...")
try:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    ts_data = ek.get_timeseries(
        rics=[ric],
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        interval='monthly'
    )
    
    if ts_data is not None and not ts_data.empty:
        print(f"  ✅ 時系列データ取得成功")
        print(f"     データ期間: {ts_data.index.min().strftime('%Y-%m')} ～ {ts_data.index.max().strftime('%Y-%m')}")
        print(f"     データ点数: {len(ts_data)}ポイント")
        print(f"     カラム: {list(ts_data.columns)}")
        
        # 最新数ポイントを表示
        print(f"\n  📊 最新データ（直近5ポイント）:")
        recent_data = ts_data.tail(5)
        for idx, row in recent_data.iterrows():
            close_val = row.get('CLOSE', 'N/A')
            print(f"     {idx.strftime('%Y-%m')}: {close_val}")
        
        # 生産量レベル分析
        if 'CLOSE' in ts_data.columns:
            latest_production = ts_data['CLOSE'].iloc[-1]
            print(f"\n  🎯 最新月次生産量: {latest_production}")
            
            if pd.notna(latest_production) and isinstance(latest_production, (int, float)):
                if 50000 <= latest_production <= 200000:  # トン/月
                    print(f"     → 合理的レベル（{latest_production:,.0f}トン/月）")
                elif 50 <= latest_production <= 200:  # kt/月
                    print(f"     → kt単位の可能性（{latest_production}kt/月 = {latest_production*1000:,.0f}トン/月）")
                elif latest_production < 50:
                    print(f"     → 極小値（{latest_production}）- 単位要確認")
                else:
                    print(f"     → 大値（{latest_production}）- 単位要確認")
        
    else:
        print(f"  ❌ 時系列データなし")
        
except Exception as e:
    print(f"  ⚠️  時系列データ例外: {e}")

# 3. 四半期データテスト
print(f"\n📈 時系列データテスト（四半期、過去3年）...")
try:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1095)  # 3年
    
    ts_quarterly = ek.get_timeseries(
        rics=[ric],
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        interval='quarterly'
    )
    
    if ts_quarterly is not None and not ts_quarterly.empty:
        print(f"  ✅ 四半期データ取得成功")
        print(f"     データ期間: {ts_quarterly.index.min().strftime('%Y-Q%q')} ～ {ts_quarterly.index.max().strftime('%Y-Q%q')}")
        print(f"     データ点数: {len(ts_quarterly)}ポイント")
        
        print(f"\n  📊 四半期データ（全期間）:")
        for idx, row in ts_quarterly.iterrows():
            close_val = row.get('CLOSE', 'N/A')
            quarter = f"Q{((idx.month-1)//3)+1}"
            print(f"     {idx.year}-{quarter}: {close_val}")
        
    else:
        print(f"  ❌ 四半期データなし")
        
except Exception as e:
    print(f"  ⚠️  四半期データ例外: {e}")

# 結果サマリー
print(f"\n=== 検証結果サマリー ===")
print(f"RIC: {ric}")
print(f"説明: {description}")

print(f"\n🌟 Escondida鉱山の重要性:")
print("- 世界最大の銅鉱山（年産約100万トン）")
print("- 全世界銅生産の約5%")
print("- BHP Billiton（57.5%）+ Rio Tinto（30%）運営")
print("- チリ・アタカマ砂漠・標高3,100m")
print("- 2017年ストライキで銅価格急騰の前例")

print(f"\n💡 データ活用価値（ディレイがあっても）:")
print("✅ 生産トレンド分析（季節性・長期傾向）")
print("✅ ストライキ・メンテナンス影響の定量化")
print("✅ 設備投資・拡張計画の効果測定")
print("✅ 競合鉱山との生産性比較")
print("✅ チリ全体の銅生産動向代理指標")
print("✅ 中長期サプライ予測の基礎データ")

print(f"\n🔧 実装推奨度: ⭐⭐⭐⭐⭐")
print("データが取得できれば、間違いなく追加すべき最重要指標")

print(f"\n=== テスト完了 ===")