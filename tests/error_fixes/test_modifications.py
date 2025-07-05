#!/usr/bin/env python3
"""
lme_daily_report.pyの修正内容の動作確認テスト
1. TURNOVER削除確認
2. 建玉（OPINT_1）取得確認
3. スズ先物16ヶ月制限確認
"""

import sys
import json
from datetime import datetime

# lme_daily_reportモジュールをインポート
from lme_daily_report import LMEReportGenerator

print("=== LME Daily Report 修正内容の動作確認 ===")
print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# config.json読み込み
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# レポート生成器のインスタンス作成
generator = LMEReportGenerator(config_path='config.json')

# 1. 取引量データ（建玉含む）の取得テスト
print("--- 1. 取引量・建玉データ取得テスト ---")
try:
    volume_data = generator.get_volume_data()
    
    for metal, data in volume_data.items():
        print(f"\n{metal}:")
        print(f"  出来高: {data.get('volume', 'N/A')}")
        print(f"  建玉: {data.get('open_interest', 'N/A')}")
        
        # turnoverフィールドが存在しないことを確認
        if 'turnover' in data:
            print(f"  ❌ エラー: turnoverフィールドが残っている！")
        else:
            print(f"  ✅ OK: turnoverフィールドは削除されている")
            
except Exception as e:
    print(f"エラー: {e}")

# 2. スズ先物の期限制限確認
print("\n\n--- 2. スズ先物16ヶ月制限テスト ---")
try:
    # 第3水曜日生成テスト
    from lme_daily_report import LMEReportGenerator
    today = datetime.now()
    
    # 銅（24ヶ月）の第3水曜日
    copper_wednesdays = generator._get_third_wednesdays(today, 24)
    print(f"銅の第3水曜日数: {len(copper_wednesdays)} （24ヶ月分）")
    
    # スズのRIC生成時の制限確認
    print("\nフォワードカーブデータ取得中...")
    forward_data = generator.get_forward_curve_data()
    
    if 'Tin' in forward_data:
        tin_data = forward_data['Tin']
        if 'curve_data' in tin_data:
            tin_rics = list(tin_data['curve_data'].keys())
            print(f"\nスズのRIC数: {len(tin_rics)}")
            print(f"最初のRIC: {tin_rics[0] if tin_rics else 'なし'}")
            print(f"最後のRIC: {tin_rics[-1] if tin_rics else 'なし'}")
            
            # 16ヶ月以内かチェック
            if len(tin_rics) <= 16:
                print("✅ OK: スズのRICは16ヶ月以内に制限されている")
            else:
                print(f"❌ エラー: スズのRICが16ヶ月を超えている（{len(tin_rics)}ヶ月）")
                
except Exception as e:
    print(f"エラー: {e}")

print("\n=== テスト完了 ===")