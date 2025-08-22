#!/usr/bin/env python3
"""
Numeron Game Launcher
Flaskアプリケーションを起動するためのスクリプト
"""

import os
import sys

# バックエンドディレクトリをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 環境変数を設定
os.environ.setdefault('FLASK_ENV', 'development')

# Flaskアプリケーションをインポートして起動
from app import app

if __name__ == '__main__':
    print("🚀 Numeron Game を起動しています...")
    print("📍 ブラウザで http://localhost:3000 にアクセスしてください")
    print("⏹️  停止するには Ctrl+C を押してください")
    print("-" * 50)
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )
