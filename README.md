# Numeron Game

3桁のユニークな数字を使って推理し合う「Numer0n」のルールをWeb上で再現するシングルプレイアプリ。CPU対戦、ターン制、ブラウザで完結します。

## プロジェクト構造

```
numer0n/
├── backend/
│   ├── app.py            # Flaskサーバー（メインロジック）
│   ├── config.py         # 設定ファイル
│   ├── env_example.txt   # 環境変数サンプル
│   ├── logs/             # バックエンドログ保存用ディレクトリ
│   └── requirements.txt  # Python依存関係
├── frontend/
│   ├── static/
│   │   ├── game_item.js  # アイテム機能
│   │   └── game_memo.js  # メモ機能
│   └── templates/
│       └── game.html     # メインゲーム画面
├── logs/                 # ルートログ保存用ディレクトリ
└── README.md
```

## セットアップ

1. **依存関係のインストール**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **サーバーの起動**
   ```bash
   python app.py
   ```

3. **ブラウザでアクセス**
   ```
   http://localhost:3000
   ```

## 遊び方

### 基本ルール
- 3桁のユニークな数字（例: 123, 405）を入力
- **EAT**: 桁も数字も一致
- **BITE**: 数字のみ一致
- 3 EATで正解！

### アイテム機能
- **GIVEUP**: 答えを公開し、ゲーム続行（メモリセット）

### メモ機能
- 0~9ボタンでグレーON/OFF切り替え
- 3EAT達成時とGIVEUP使用時に自動リセット

### ゲーム動作
- ターン制（数字入力時のみカウントアップ）
- 1ターンにアイテム1個まで使用可能
- 3EAT達成後もゲーム継続

## 技術スタック

- **Backend**: Python + Flask
- **Frontend**: HTML + CSS + JavaScript + Jinja2
- **Port**: 3000

## 実行系統

- Python (Flask)
- JavaScript (Vanilla)
- HTML/CSS (1ページ構成) 