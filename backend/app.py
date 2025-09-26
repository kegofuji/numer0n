import os
import logging
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from dotenv import load_dotenv
import random
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from numeron_game import NumeronGame, GameMode, HumanPlayer, AIPlayer, Item, ItemType

# 環境変数を読み込み
load_dotenv()

# ----------------------------------------
# 設定クラス
# ----------------------------------------
class Config:
    """基本設定クラス"""
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-key")
    DEBUG = os.environ.get("DEBUG", "True") == "True"
    TESTING = False
    
    # データベース設定
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///numeron.db'
    
    # セッション設定
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # HTTPS環境ではTrueに変更
    
    # アプリケーション設定
    MAX_TURNS = 12
    NUMBER_LENGTH = 3
    
    # ログ設定
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/numeron.log'

class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    DATABASE_URL = 'sqlite:///numeron_dev.db'

class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Render環境での設定
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """テスト環境設定"""
    TESTING = True
    DATABASE_URL = 'sqlite:///numeron_test.db'

# 設定辞書
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# ----------------------------------------
# Flask アプリケーションファクトリ
# ----------------------------------------
def create_app(config_name=None):
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
    app.config.from_object(config[config_name])
    
    # 環境変数から設定を取得
    app.secret_key = os.environ.get("SECRET_KEY", "default-key")
    app.config["DEBUG"] = os.environ.get("DEBUG", "True") == "True"
    
    setup_logging(app)
    return app

# ----------------------------------------
# ログ設定
# ----------------------------------------
def setup_logging(app):
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL'], logging.INFO),
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
        handlers=[
            logging.FileHandler(app.config['LOG_FILE']),
            logging.StreamHandler()
        ]
    )

# ----------------------------------------
# アプリケーションインスタンス生成
# ----------------------------------------
app = create_app()

# ----------------------------------------
# ユーティリティ関数
# ----------------------------------------
def generate_computer_number():
    digits = list(range(10))
    random.shuffle(digits)
    if digits[0] == 0:
        for i in range(1, 10):
            if digits[i] != 0:
                digits[0], digits[i] = digits[i], digits[0]
                break
    return digits[:3]

def judge(answer, guess):
    eat = sum(a == g for a, g in zip(answer, guess))
    bite = sum(min(answer.count(d), guess.count(d)) for d in set(guess)) - eat
    return eat, bite

def calculate_eat_bite(answer, guess):
    """EAT/BITE計算"""
    eat = sum(a == g for a, g in zip(answer, guess))
    bite = sum(min(answer.count(d), guess.count(d)) for d in set(guess)) - eat
    return eat, bite

def is_valid_number(number_str):
    if len(number_str) != 3 or not number_str.isdigit():
        return False, "3桁の数字を入力してください"
    if len(set(number_str)) != 3:
        return False, "数字の重複は禁止です"
    return True, ""

def use_item(item_name, computer_number, target_digit=None):
    if item_name == 'GIVEUP':
        return {
            'effect': f"GIVE UP! 答えは {''.join(map(str, computer_number))} です",
            'answer': ''.join(map(str, computer_number)),
            'game_ended': True,
            'hide_message': True
        }
    return {'effect': "不明なアイテムです"}

# ----------------------------------------
# ルーティング処理
# ----------------------------------------
@app.route('/')
def index():
    """ゲームモード選択画面"""
    return render_template('index.html')

@app.route('/game')
def game():
    """ゲーム画面"""
    mode = request.args.get('mode', 'single')
    new_game = request.args.get('new', 'false') == 'true'
    
    if 'game_mode' not in session or session['game_mode'] != mode or new_game:
        # 新しいゲームを開始
        session.clear()
        session['game_mode'] = mode
        session['game'] = None
        session['turn'] = 1
        session['current_player'] = 'プレイヤー1'
        session['game_ended'] = False
        session['winner'] = None
        session['message'] = ''
        session['message_type'] = 'info'
        session['item_used_this_turn'] = False
        
        # ゲームデータをセッションに保存（オブジェクトではなくデータのみ）
        if mode == 'single':
            session['player1_number'] = [1, 5, 8]  # プレイヤー番号
            session['player2_number'] = [6, 3, 4]  # AI番号
            session['numbers_set'] = True
        else:
            # 2人用の場合は番号未設定
            session['player1_number'] = None
            session['player2_number'] = None
            session['numbers_set'] = False
            session['number_setting_player'] = 'プレイヤー1'
        
        session['player1_history'] = []
        session['player2_history'] = []
        session['player1_items'] = [{'name': 'DOUBLE', 'used': False}, {'name': 'HIGH&LOW', 'used': False}, 
                                   {'name': 'TARGET', 'used': False}, {'name': 'SLASH', 'used': False},
                                   {'name': 'SHUFFLE', 'used': False}, {'name': 'CHANGE', 'used': False}]
        session['player2_items'] = [{'name': 'DOUBLE', 'used': False}, {'name': 'HIGH&LOW', 'used': False}, 
                                   {'name': 'TARGET', 'used': False}, {'name': 'SLASH', 'used': False},
                                   {'name': 'SHUFFLE', 'used': False}, {'name': 'CHANGE', 'used': False}]
        session['player1_memo'] = [False] * 10
        session['player2_memo'] = [False] * 10
        session.modified = True
    
    # 2人用で番号が未設定の場合は番号設定画面を表示
    if mode == 'two' and not session.get('numbers_set', False):
        return render_number_setting_page()
    
    return render_game_page()

@app.route('/game', methods=['POST'])
def game_post():
    """ゲーム操作の処理"""
    action = request.form.get('action')
    
    if action == 'set_number':
        handle_number_setting()
    elif action == 'guess':
        handle_guess()
    elif action == 'item':
        handle_item_use()
    elif action == 'giveup':
        handle_giveup()
    
    # 2人用で番号が未設定の場合は番号設定画面を表示
    if session['game_mode'] == 'two' and not session.get('numbers_set', False):
        return render_number_setting_page()
    
    return render_game_page()

def handle_guess():
    """推測の処理"""
    digit1 = request.form.get('digit1')
    digit2 = request.form.get('digit2')
    digit3 = request.form.get('digit3')
    player = request.form.get('player')
    
    if not all([digit1, digit2, digit3]):
        session['message'] = '3桁の数字を入力してください'
        session['message_type'] = 'error'
        return
    
    guess = [int(digit1), int(digit2), int(digit3)]
    
    if len(set(guess)) != 3:
        session['message'] = '数字の重複は禁止です'
        session['message_type'] = 'error'
        return
    
    # フォームから送信されたプレイヤー情報を使用
    if player == 'player1' or session['current_player'] == 'プレイヤー1':
        current_number = session['player1_number']
        opponent_number = session['player2_number']
        current_history = session['player1_history']
        current_memo = session['player1_memo']
        next_player = 'プレイヤー2' if session['game_mode'] == 'two' else 'AI'
    else:
        current_number = session['player2_number']
        opponent_number = session['player1_number']
        current_history = session['player2_history']
        current_memo = session['player2_memo']
        next_player = 'プレイヤー1'
    
    # EAT/BITE計算
    eat, bite = calculate_eat_bite(opponent_number, guess)
    
    # 履歴に追加
    current_history.append({
        'guess': guess,
        'eat': eat,
        'bite': bite,
        'effect': ''
    })
    
    # メモカード更新
    for digit in guess:
        current_memo[digit] = True
    
    session['message'] = f"推測: {''.join(map(str, guess))} → {eat}EAT {bite}BITE"
    session['message_type'] = 'success' if eat == 3 else 'info'
    
    # 勝利判定
    if eat == 3:
        session['game_ended'] = True
        session['winner'] = session['current_player']
        session['message'] = f"🎉 {session['current_player']}の勝利！"
        session['message_type'] = 'success'
    else:
        # ターン終了処理
        session['turn'] += 1
        session['current_player'] = next_player
        session['item_used_this_turn'] = False
    
    session.modified = True

def handle_item_use():
    """アイテム使用の処理"""
    item_name = request.form.get('item_name')
    
    if session['item_used_this_turn']:
        session['message'] = 'このターンでは既にアイテムを使用しました'
        session['message_type'] = 'error'
        return
    
    # 現在のプレイヤーのアイテムを取得
    if session['current_player'] == 'プレイヤー1':
        current_items = session['player1_items']
        current_history = session['player1_history']
        opponent_number = session['player2_number']
    else:
        current_items = session['player2_items']
        current_history = session['player2_history']
        opponent_number = session['player1_number']
    
    # アイテムを検索
    item = None
    for i in current_items:
        if i['name'] == item_name and not i['used']:
            item = i
            break
    
    if not item:
        session['message'] = 'アイテムが見つからないか、既に使用済みです'
        session['message_type'] = 'error'
        return
    
    # アイテム使用
    item['used'] = True
    session['item_used_this_turn'] = True
    
    # アイテム効果を処理
    effect = process_item_effect(item_name, opponent_number)
    
    # 履歴に追加
    current_history.append({
        'guess': None,
        'eat': 0,
        'bite': 0,
        'effect': f"{item_name}アイテム: {effect}"
    })
    
    session['message'] = f"{item_name}アイテムを使用しました: {effect}"
    session['message_type'] = 'info'
    
    session.modified = True

def handle_number_setting():
    """番号設定の処理"""
    digit1 = request.form.get('digit1')
    digit2 = request.form.get('digit2')
    digit3 = request.form.get('digit3')
    
    if not all([digit1, digit2, digit3]):
        session['message'] = '3桁の数字を入力してください'
        session['message_type'] = 'error'
        return
    
    number = [int(digit1), int(digit2), int(digit3)]
    
    if len(set(number)) != 3:
        session['message'] = '数字の重複は禁止です'
        session['message_type'] = 'error'
        return
    
    # 現在の設定プレイヤーに番号を設定
    if session['number_setting_player'] == 'プレイヤー1':
        session['player1_number'] = number
        session['number_setting_player'] = 'プレイヤー2'
        session['message'] = f"プレイヤー1の番号を設定しました。次はプレイヤー2の番号を設定してください。"
        session['message_type'] = 'info'
    else:
        session['player2_number'] = number
        session['numbers_set'] = True
        session['message'] = f"プレイヤー2の番号を設定しました。ゲームを開始します！"
        session['message_type'] = 'success'
    
    session.modified = True

def handle_giveup():
    """GIVE UPの処理"""
    # 現在のプレイヤーと対戦相手を決定
    if session['current_player'] == 'プレイヤー1':
        current_history = session['player1_history']
        opponent_number = session['player2_number']
        winner = 'プレイヤー2' if session['game_mode'] == 'two' else 'AI'
    else:
        current_history = session['player2_history']
        opponent_number = session['player1_number']
        winner = 'プレイヤー1'
    
    session['game_ended'] = True
    session['winner'] = winner
    session['message'] = f"GIVE UP! {session['current_player']}の敗北。{winner}の勝利！"
    session['message_type'] = 'error'
    
    # 履歴に追加
    current_history.append({
        'guess': None,
        'eat': 0,
        'bite': 0,
        'effect': f"GIVE UP! 答えは {''.join(map(str, opponent_number))} でした"
    })
    
    session.modified = True

def process_item_effect(item_name, opponent_number):
    """アイテム効果を処理"""
    if item_name == "DOUBLE":
        return "2回連続コール可能。ただし1桁開示。"
    elif item_name == "HIGH&LOW":
        high_low_info = []
        for i, digit in enumerate(opponent_number):
            if digit >= 5:
                high_low_info.append("H")
            else:
                high_low_info.append("L")
        return "各桁のHIGH/LOW情報: " + "".join(high_low_info)
    elif item_name == "TARGET":
        target_digit = random.randint(0, 9)
        if target_digit in opponent_number:
            pos = opponent_number.index(target_digit)
            return f"数字{target_digit}は{pos+1}桁目にあります"
        else:
            return f"数字{target_digit}は含まれていません"
    elif item_name == "SLASH":
        max_digit = max(opponent_number)
        min_digit = min(opponent_number)
        slash_number = max_digit - min_digit
        return f"スラッシュナンバー: {slash_number}"
    elif item_name == "SHUFFLE":
        return "自分の番号を並べ替えました"
    elif item_name == "CHANGE":
        return "自分の番号の1桁を変更しました"
    else:
        return "不明なアイテムです"

def render_number_setting_page():
    """番号設定画面のレンダリング"""
    return render_template('number_setting.html',
                           setting_player=session['number_setting_player'],
                           message=session['message'],
                           message_type=session['message_type'])

def render_game_page():
    """ゲーム画面のレンダリング"""
    mode = session['game_mode']
    
    # 両プレイヤーのアイテム情報を準備
    player1_items = session['player1_items'].copy()
    player2_items = session['player2_items'].copy()
    
    # アイテムタイプを追加
    for item in player1_items:
        if item['name'] in ['DOUBLE', 'HIGH&LOW', 'TARGET', 'SLASH']:
            item['type'] = '攻撃系'
        else:
            item['type'] = '防御系'
    
    for item in player2_items:
        if item['name'] in ['DOUBLE', 'HIGH&LOW', 'TARGET', 'SLASH']:
            item['type'] = '攻撃系'
        else:
            item['type'] = '防御系'
    
    # 履歴情報を準備（プレイヤー別）
    player1_history = []
    player2_history = []
    
    for call in session['player1_history']:
        player1_history.append({
            'guess': call['guess'],
            'eat': call['eat'],
            'bite': call['bite'],
            'effect': call.get('effect', '')
        })
    
    for call in session['player2_history']:
        player2_history.append({
            'guess': call['guess'],
            'eat': call['eat'],
            'bite': call['bite'],
            'effect': call.get('effect', '')
        })
    
    # 現在のプレイヤーのメモカード
    if session['current_player'] == 'プレイヤー1':
        memo_cards = session['player1_memo']
    else:
        memo_cards = session['player2_memo']
    
    return render_template('game_with_items.html',
                           mode=mode,
                           turn=session['turn'],
                           current_player=session['current_player'],
                           player1_items=player1_items,
                           player2_items=player2_items,
                           player1_history=player1_history,
                           player2_history=player2_history,
                           memo_cards=memo_cards,
                           message=session['message'],
                           message_type=session['message_type'],
                           game_ended=session['game_ended'],
                           winner=session['winner'],
                           item_used_this_turn=session['item_used_this_turn'])


# ----------------------------------------
# サーバ起動
# ----------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)