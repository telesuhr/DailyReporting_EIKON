#!/usr/bin/env python3
"""
中国工業生産指数の代替RIC探索
"""

import eikon as ek
import json
import warnings

warnings.filterwarnings('ignore')

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

ek.set_app_key(config['eikon_api_key'])

# 中国工業生産指数の代替RIC候補
alternative_rics = {
    # 様々なフォーマット
    'aCNIACT.C': '中国鉱工業生産指数（ドット形式）',
    'CNPIACT.C': '中国鉱工業生産指数（aなし）', 
    'CNIPACTY.C': '中国工業生産年次',
    'CNIPM=ECI': '中国工業生産月次（ECI）',
    'CHIND=ECI': '中国工業指数（ECI）',
    'CH.IP': '中国工業生産（省略形）',
    'CNINDY=ECI': '中国工業年次（ECI）',
    'CNIND.C': '中国工業指数（C形式）',
    'CNINDT=ECI': '中国工業生産（T形式）',
    'CHINDPRO=': '中国工業生産（等号形式）'
}

print("=== 中国工業生産指数 代替RIC探索 ===")

successful_rics = []

for ric, description in alternative_rics.items():
    print(f"\n--- {ric} ({description}) ---")
    
    try:
        # まず基本フィールドテスト
        df, err = ek.get_data(ric, ['CF_LAST', 'CF_DATE'])
        
        if err:
            print(f"  警告: {err}")
        
        if df is not None and not df.empty:
            # データがあるかチェック
            has_data = False
            for col in df.columns:
                if col != 'Instrument':
                    value = df[col].iloc[0]
                    if value is not None and str(value) != 'nan' and str(value) != '<NA>':
                        print(f"  ✅ {col}: {value}")
                        has_data = True
                        
            if has_data:
                successful_rics.append((ric, description))
                
                # 時系列テストも試行
                try:
                    from datetime import datetime, timedelta
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30)
                    
                    ts_data = ek.get_timeseries(
                        rics=[ric],
                        start_date=start_date.strftime('%Y-%m-%d'),
                        end_date=end_date.strftime('%Y-%m-%d'),
                        interval='daily'
                    )
                    
                    if ts_data is not None and not ts_data.empty:
                        print(f"  ✅ 時系列データ: {len(ts_data)}日分")
                        latest = ts_data['CLOSE'].iloc[-1] if 'CLOSE' in ts_data.columns else None
                        if latest:
                            print(f"  最新値: {latest}")
                    else:
                        print(f"  ⚠️  時系列データなし")
                        
                except Exception as ts_e:
                    print(f"  ⚠️  時系列エラー: {ts_e}")
                    
            else:
                print(f"  ○ RIC有効だがデータなし")
        else:
            print(f"  ❌ レスポンスなし")
            
    except Exception as e:
        print(f"  ❌ エラー: {e}")

print(f"\n=== 結果サマリー ===")
if successful_rics:
    print("✅ 使用可能なRIC:")
    for ric, desc in successful_rics:
        print(f"  - {ric}: {desc}")
else:
    print("❌ 有効なRICが見つかりませんでした")
    print("\n他の指標（固定資産投資、PPI等）を試すことをお勧めします")