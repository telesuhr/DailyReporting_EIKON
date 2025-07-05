# Workspace検索推奨キーワード - LMEサプライチェーンデータ

## 直接生産統計データ（高優先度）

### 鉱山生産データ
- `copper mine production`
- `mine production data`
- `copper output statistics`
- `mining production figures`

### 地域別生産統計
- `Chile copper production`
- `Peru copper mining output`
- `China copper production`
- `Australia copper production`

### 精錬・製錬データ
- `smelter capacity utilization`
- `refinery production data`
- `copper smelting statistics`
- `refined copper production`

## 企業決算・ガイダンスデータ（中優先度）

### 主要鉱山会社
- `Freeport production guidance`
- `BHP copper production`
- `Vale base metals production`
- `Glencore copper segment`
- `Rio Tinto copper operations`
- `Antofagasta copper output`
- `Southern Copper production`

### 決算関連
- `quarterly production reports`
- `annual production guidance`
- `mining company earnings`
- `copper production forecasts`

## 業界統計・分析データ（中優先度）

### 主要統計機関
- `ICSG copper statistics`
- `WBMS copper data`
- `CRU copper intelligence`
- `Wood Mackenzie copper`
- `Antaike copper statistics`

### 業界レポート
- `copper market analysis`
- `mining industry reports`
- `copper supply demand balance`
- `global copper statistics`

## 処理料金・マージンデータ（高優先度）

### TC/RC料金
- `copper TC RC benchmark`
- `smelter treatment charge`
- `copper concentrate price`
- `refining charges copper`

### マージン指標
- `smelting margin`
- `refining spread`
- `concentrate premium`

## 在庫・流通データ（高優先度）

### 倉庫在庫
- `copper warehouse stocks`
- `bonded warehouse inventory`
- `port inventory data`
- `regional stock levels`

### 流通統計
- `copper shipments`
- `trade flow data`
- `import export statistics`
- `copper logistics`

## コスト・マージンデータ（中優先度）

### 生産コスト
- `copper production costs`
- `mining cash costs`
- `all-in sustaining costs`
- `energy costs mining`

### エネルギー・電力
- `Chile electricity prices`
- `mining energy costs`
- `smelter power consumption`

## 検索戦略

### 1. 直接RIC検索
最初に具体的なRICコードを検索：
- `MCU PROD`（LME生産関連）
- `CU PROD CHILE`（チリ銅生産）
- `COPPER TC RC`（処理料金）

### 2. データプロバイダー検索
主要データソースから探索：
- `ICSG` (International Copper Study Group)
- `WBMS` (World Bureau of Metal Statistics)
- `CRU` (CRU Group)
- `SMM` (Shanghai Metals Market)

### 3. 企業・取引所検索
- `FCX` (Freeport-McMoRan)
- `BHP` (BHP Group)
- `VALE` (Vale SA)
- `GLEN` (Glencore)

## 発見時の対応

### 有効RICが見つかった場合
1. テストスクリプトで動作確認
2. `config.json`に追加
3. `lme_daily_report.py`に統合
4. 完全テスト実行

### データが見つからない場合
既存の間接指標（企業株価・ETF）を活用：
- 主要鉱山会社株価 (FCX.N, VALE.N, BHP.AX等)
- セクターETF (XME, DJP)
- 相関分析による代替指標作成

## 実装済み代替指標

すでに`config.json`に追加済み：
- 主要鉱山会社7社の株価データ
- 鉱業セクターETF 2銘柄
- 間接的サプライチェーン分析機能

これらは生産問題・設備投資・操業状況の先行指標として活用可能。