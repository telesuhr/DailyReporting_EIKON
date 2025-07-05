# エラー修正テストファイル

このディレクトリには、LME日次レポートシステムのエラー修正プロセスで作成されたテストファイルが含まれています。

## 修正完了項目

### 1. 中国経済指標修正
- `test_china_indicators.py` - 中国PMI・経済指標の包括的テスト
- `test_china_alternatives.py` - 工業生産指数の代替RIC探索
- `test_china_fields.py` - 中国指標の正しいフィールド探索
- `test_china_industrial.py` - 鉱工業生産指数テスト
- `test_cnio_variants.py` - CNIO系RICの動作確認

**結果**: `CNPMIB=ECI` (中国国家統計局製造業PMI) を採用

### 2. COMEX在庫データ修正
- `test_comex_fields.py` - COMEX銅在庫の正しいフィールド探索
- `test_comex_simple.py` - 実際のレポートと同じ方法でのテスト

**結果**: `HG-STX-COMEX` + `CF_LAST`フィールドで正常動作確認（220,954トン）

### 3. マクロ経済指標修正
- `test_vix_alternatives.py` - VIX代替RICテスト
- `test_us10y_alternatives.py` - 米国10年債利回り代替RICテスト
- `test_us10yt_details.py` - US10YT=RRの詳細確認
- `test_gold_price.py` - 金価格取得とCopper/Gold Ratio計算

**結果**: 
- VIX: `.VIXIE` (CBOE Europe Volatility Index) を採用
- US10Y: `US10YT=RR` を採用
- Gold: `XAU=` を採用（Copper/Gold Ratioを動的計算）

### 4. その他修正
- `test_modifications.py` - TURNOVER削除とTin制限の確認
- `test_open_interest.py` - 建玉データ(OPINT_1)の動作確認
- `test_shfe_smm_inventory.py` - SHFE・SMM在庫データの包括検証

**結果**: 
- Tinスズ先物16ヶ月制限適用
- TURNOVER削除、OPINT_1(建玉)で置換
- SHFE在庫全6金属正常、SMM在庫は銅のみ使用

## 最終状態

すべてのエラー修正が完了し、LME日次レポートシステムは正常動作中。
2025年7月5日分のレポート生成に成功。

## ファイル整理

2025年7月5日にルートディレクトリから `tests/error_fixes/` ディレクトリに移動・整理済み。