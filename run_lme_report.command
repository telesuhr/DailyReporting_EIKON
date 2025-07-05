#!/bin/bash
# LME Daily Report - ダブルクリックで実行可能

# ターミナルウィンドウのタイトル設定
echo -e "\033]0;LME Daily Report Generator\007"

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# 実行開始の通知
echo "🚀 LME Daily Report Generator を開始します..."
echo

# メインスクリプトの実行
./run_report.sh

# 実行後の処理
echo
echo "📊 レポートが生成されました！"
echo "📁 output フォルダを確認してください。"
echo
echo "⏳ 10秒後にウィンドウが自動で閉じます..."
echo "   今すぐ閉じる場合は Cmd+W を押してください"

# 結果表示のための待機
for i in {10..1}; do
    echo -n "."
    sleep 1
done

echo
echo "✅ 完了！"