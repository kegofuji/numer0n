# Numeron Game

3桁のユニークな数字を当てるゲームです。

## プロジェクト構造

```
numeron/
├── backend/
│   ├── app.py          # Flaskサーバー（メインロジック）
│   └── requirements.txt # Python依存関係
├── frontend/
│   └── templates/
│       └── index.html   # HTMLテンプレート
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

- 3桁のユニークな数字（例: 123, 405）を入力
- **EAT**: 桁も数字も一致
- **BITE**: 数字のみ一致
- 3 EATで正解！

## 技術スタック

- **Backend**: Python + Flask
- **Frontend**: HTML + CSS + Jinja2
- **Port**: 3000 