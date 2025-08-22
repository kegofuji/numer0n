#!/bin/bash

echo "🚀 Numeron Game を起動しています..."

# 仮想環境が存在する場合はアクティベート
if [ -d "venv" ]; then
    echo "📦 仮想環境をアクティベートしています..."
    source venv/bin/activate
fi

# 必要なパッケージがインストールされているかチェック
echo "🔍 必要なパッケージをチェックしています..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 必要なパッケージをインストールしています..."
    pip3 install -r backend/requirements.txt
fi

# アプリケーションを起動
echo "🌟 アプリケーションを起動しています..."
echo "📍 ブラウザで http://localhost:5000 にアクセスしてください"
echo "⏹️  停止するには Ctrl+C を押してください"
echo "-" * 50

python3 run.py
