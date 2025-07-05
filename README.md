# LME日次レポート生成システム

**プロフェッショナル向けLME（ロンドン金属取引所）日次マーケットレポート自動生成システム**

## 🎯 概要

このシステムは、LME金属（銅、アルミニウム、亜鉛、鉛、ニッケル、スズ）の包括的な日次マーケットレポートを生成し、プロフェッショナルトレーダーや機関投資家を対象としています。LME、上海先物取引所（SHFE）、CMEなど複数のソースからデータを収集し、Claude AI分析に最適化された詳細分析レポートを生成します。

## ⚡ クイックスタート

### 簡単実行
```bash
# Linux/macOS（自動環境セットアップ）
./run_report.sh

# macOS（ダブルクリック実行）
./run_lme_report.command

# Windows（自動環境セットアップ）
run_report.bat

# 手動実行
python lme_daily_report.py
```

### 出力
- **レポートファイル**: `output/LME_Daily_Report_Input_YYYYMMDD.txt`
- **ログファイル**: `logs/lme_report_YYYYMMDD.log`

## 🔧 主要機能

### マーケットデータカバレッジ
- **LME 6金属**: 価格データ、在庫、取引量、フォワードカーブ
- **ファンドポジション**: 機関投資家のロング・ショートポジション
- **マルチ取引所比較**: LME vs 上海 vs CME銅カーブ
- **上海プレミアム**: 3大指標（洋山港、CIF、保税倉庫）
- **マクロ環境**: USD指数、利回り、VIX、株式市場
- **ニュース統合**: 3日間包括的ニュース収集・優先度フィルタリング

### 高度な分析機能
- **動的RIC生成**: 実行日に基づくLME契約RICの自動更新
- **ワラント分析**: LMEワラントの詳細内訳（オンワラント、キャンセル、比率）
- **取引所間裁定**: 価格差の自動検出
- **トレンド分析**: 5日、20日移動パターンと統計的有意性

## 📊 システム構成

```
LME日次レポート生成システム
├── lme_daily_report.py          # メインシステム
├── config.json                  # 設定ファイル（RIC、設定）
├── requirements.txt             # 依存関係
├── run_lme_report.command       # macOS自動実行スクリプト
├── run_report.sh/bat           # Linux/Windows自動実行スクリプト
├── output/                     # 生成レポート
├── logs/                       # 実行ログ
├── tests/                      # テストスクリプト
│   ├── error_fixes/            # エラー修正テスト
│   └── ...                     # その他テスト
├── development_scripts/        # 開発ユーティリティ
├── docs/                       # ドキュメント
├── CopperSpreadAnalyzer/       # 統合スプレッド分析
├── CopperSpreadAnalyzer_Standalone/  # スタンドアロン版
└── RefinitivDataExplorer/      # データ探索ツール
```

## 🛠 インストール

### 必要条件
- Python 3.8+
- Refinitiv Eikon Desktop（実行中）
- 有効なEikon APIキー

### 依存関係
```bash
pip install -r requirements.txt
```

**主要パッケージ**: `eikon`, `pandas`, `numpy`  
**オプション**: `python-dotenv`, `openpyxl`, `colorlog`

## ⚙️ 設定

### API設定
1. `config.json`にEikon APIキーを設定:
```json
{
  "eikon_api_key": "あなたの実際のAPIキー"
}
```

2. Eikon Desktopが実行中で接続されていることを確認

### カスタマイズ
- **ニュース設定**: ニュース収集の有効/無効化
- **市場休日**: カスタム休日日付の追加
- **RIC代替**: 信頼性のためのフォールバックRIC設定

## 📈 レポート構造

### Claude分析用（2000-3000語）
1. **銅市場詳細分析**（主要フォーカス）
   - マルチ取引所価格比較と裁定機会
   - 期間構造分析（1-6ヶ月）
   - 在庫動向とワラント分析
   - ファンドポジショニングとセンチメント分析

2. **トレーディング戦略セクション**
   - カレンダースプレッド戦略（1M-3M、3M-6M）
   - 地域間スプレッド分析（LME-上海、LME-CME）
   - アウトライト取引推奨
   - リスク管理ガイドライン

3. **マーケットコンテキスト**
   - 他金属相関分析
   - マクロ環境影響
   - 市場示唆付きニュース分析
   - 前向きな洞察

## 🚀 高度な機能

### マルチ取引所統合
- **LME**: 動的月次契約生成（MCU+月+年）
- **SHFE**: SCFc1-c12契約とCNY→USD変換
- **CME**: HGc1-c12契約とセント/ポンド→USD/MT変換

### データ品質保証
- 包括的エラーハンドリングとリトライロジック
- 代替RICフォールバック機構
- 営業日計算（週末・祝日対応）
- API制限遵守

### 自動化対応
- クロスプラットフォーム実行スクリプト
- タスクスケジューラー統合（Windows XMLテンプレート提供）
- 仮想環境自動セットアップ
- 無人運用機能

## 📊 パフォーマンス

- **実行時間**: 4-5分（完全レポート）
- **データカバレッジ**: 95%以上の成功率
- **出力サイズ**: 約1,675行の構造化分析
- **API最適化**: インテリジェントキャッシュとバッチ処理

## 🔍 テスト

```bash
# 包括的テスト実行
cd tests/
python test_fund_positions_complete.py     # ファンドポジション検証
python test_three_exchanges_integration.py # マルチ取引所テスト
python test_dynamic_ric.py                 # 動的RIC生成

# エラー修正テスト
cd tests/error_fixes/
python test_china_indicators.py            # 中国経済指標テスト
python test_comex_fields.py                # COMEX在庫データテスト
python test_gold_price.py                  # 金価格・比率計算テスト
```

## 📚 ドキュメント

- **システムガイド**: `docs/CLAUDE.md`
- **APIリファレンス**: `docs/README.md`
- **タスクスケジューリング**: `docs/task_scheduler_template.xml`
- **エラー修正履歴**: `tests/error_fixes/README.md`

## 🔧 最新のエラー修正（2025年7月）

- **Tinスズ先物**: 16ヶ月制限適用
- **建玉データ**: OPINT_1で正常取得（TURNOVER削除）
- **VIX指標**: .VIXIEに更新
- **米国10年債**: US10YT=RRに更新
- **中国PMI**: CNPMIB=ECIに更新
- **金価格統合**: XAU=でCopper/Gold Ratio動的計算
- **在庫データ**: 全取引所正常動作確認

## 🤝 サポート

- **問題報告**: GitHub Issues
- **開発**: 分析ツールは`development_scripts/`を参照
- **テスト**: 検証スクリプトは`tests/`を参照

## 📄 ライセンス

このプロジェクトはプロフェッショナルトレーディングと機関投資家向けに設計されています。

---

**最終更新**: 2025-07-05  
**バージョン**: 3.0（包括的エラー修正完了）  
**対応**: LME/SHFE/CME マルチ取引所統合