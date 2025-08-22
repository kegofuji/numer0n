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
│   │   └── game_item.js  # アイテム機能
│   └── templates/
│       └── game.html     # メインゲーム画面
├── render.yaml           # Renderデプロイ設定
└── README.md
```

## セットアップ

### 方法1: 簡単起動（推奨）
```bash
./start.sh
```

### 方法2: 手動起動
1. **依存関係のインストール**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **サーバーの起動**
   ```bash
   # プロジェクトルートから
   python3 run.py
   
   # または、backendディレクトリから
   cd backend
   python3 app.py
   ```

3. **ブラウザでアクセス**
   ```
   http://localhost:5000
   ```

## 🚀 Renderでのデプロイ

### 事前準備
1. [Render](https://render.com/) アカウントを作成
2. GitHubリポジトリと連携

### デプロイ手順
1. **Renderダッシュボードで「New Web Service」を選択**
2. **GitHubリポジトリを選択**
3. **以下の設定を確認：**
   - **Name**: `numeron-game`（任意）
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: `Free`（無料プラン）

4. **環境変数を設定：**
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: 自動生成（または手動設定）
   - `LOG_LEVEL`: `INFO`

5. **「Create Web Service」をクリック**

### デプロイ後の確認
- デプロイが完了すると、`https://your-app-name.onrender.com` のようなURLが生成されます
- 初回アクセス時に少し時間がかかる場合があります（コールドスタート）

### 注意事項
- 無料プランでは15分間アクセスがないとスリープ状態になります
- 初回アクセス時に再起動が必要な場合があります
- ログはRenderダッシュボードで確認できます

## 遊び方

### 基本ルール
- 3桁のユニークな数字（例: 123, 405）を入力
- **EAT**: 桁も数字も一致
- **BITE**: 数字のみ一致
- 3 EATで正解！

### 入力方法
- 3つの入力フィールドに数字を入力
- 3桁揃うと「enterで結果判定」メッセージが表示
- **Enterキー**で結果判定を実行
- 半角・全角数字に対応

### アイテム機能
- **GIVEUP**: 答えを公開し、ゲーム終了

### ゲーム動作
- ターン制（数字入力時のみカウントアップ）
- 1ターンにアイテム1個まで使用可能
- 3EAT達成後もゲーム継続可能

## 技術スタック

- **Backend**: Python + Flask
- **Frontend**: HTML + CSS + JavaScript + Jinja2
- **Port**: 5000

## 実行環境

- Python (Flask)
- JavaScript (Vanilla)
- HTML/CSS (1ページ構成)

## 実装済み機能

### ✅ 完了済み
- 基本的なゲームロジック（EAT/BITE判定）
- ターン制ゲーム進行
- アイテム機能（GIVEUP）
- 履歴表示機能
- レスポンシブデザイン
- セッション管理
- ログ機能

## 未実装・未整備項目

### 🔄 メモ機能（未実装）
- プレイヤーが推測履歴にメモを追加する機能
- ヒントや戦略を記録する機能
- メモの保存・読み込み機能

### 🧪 テスト環境（未整備）
- ユニットテスト（`test_*.py`）
- 統合テスト
- テストカバレッジ
- 自動テスト実行環境

### 🔄 CI/CD（未整備）
- GitHub Actions設定
- 自動テスト実行
- 自動デプロイ
- コード品質チェック

### 🚀 運用面（未整備）
- 本番環境用設定
- ログローテーション
- エラーハンドリング強化
- セキュリティ設定強化
- パフォーマンス監視
- データベース永続化

### 📊 追加機能（検討中）
- 統計機能（勝率、平均ターン数など）
- 難易度設定
- マルチプレイヤー対応
- リーダーボード機能

## 開発状況

- **基本ゲーム機能**: 100% 完了
- **UI/UX**: 90% 完了
- **テスト環境**: 0% 未実装
- **CI/CD**: 0% 未実装
- **運用環境**: 20% 基本設定のみ

## 今後の開発予定

1. **優先度: 高**
   - テスト環境の構築
   - CI/CD設定の追加
   - メモ機能の実装

2. **優先度: 中**
   - 運用環境の整備
   - セキュリティ強化

3. **優先度: 低**
   - 追加機能の実装
   - パフォーマンス最適化 