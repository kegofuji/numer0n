# Numeron Game

3桁のユニークな数字を使って推理し合う「Numer0n」のルールをWeb上で再現するシングルプレイアプリ。CPU対戦、ターン制、ブラウザで完結します。

## プロジェクト構造

```
numeron/
├── backend/
│   ├── app.py          # Flaskサーバー（メインロジック）
│   ├── models.py       # データモデル
│   ├── config.py       # 設定ファイル
│   └── requirements.txt # Python依存関係
├── frontend/
│   ├── templates/
│   │   └── game.html   # メインゲーム画面
│   └── static/
│       ├── game_item.js # アイテム機能
│       └── game_memo.js # メモ機能
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
- **SLASH**: 第1段階の最大値 - 最小値を表示
- **GIVEUP**: 答えを公開し、ゲーム続行（メモリセット）
- **HIGH_LOW**: 各桁の値がHIGH(5-9)かLOW(0-4)かを表示
- **TARGET**: 指定した1桁の数字が含まれている場合、位置(百/十/一)を表示

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