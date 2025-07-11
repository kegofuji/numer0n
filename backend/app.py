import os
import logging
from datetime import datetime, timezone
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from dotenv import load_dotenv
from config import config
import random

# 環境変数を読み込み
load_dotenv()

# ----------------------------------------
# Flask アプリケーションファクトリ
# ----------------------------------------
def create_app(config_name=None):
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app = Flask(__name__, template_folder='../frontend/templates')
    app.config.from_object(config[config_name])
    app.secret_key = os.getenv('SECRET_KEY', 'your_default_secret_key')
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
            'answer': ''.join(map(str, computer_number))
        }
    return {'effect': "不明なアイテムです"}

# ----------------------------------------
# ルーティング処理
# ----------------------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        session.clear()
        session['computer_number'] = generate_computer_number()
        session.update({
            'history': [],
            'turn': 1,
            'used_items': [],
            'item_used_this_turn': False,
            'start_time': datetime.now(timezone.utc).isoformat()
        })
        app.logger.info(f"New game started: {session['computer_number']}")

    msg, msg_type = '', 'info'
    guess_str = request.form.get('guess')
    item = request.form.get('used_item')

    if request.method == 'POST':
        if guess_str and item:
            msg, msg_type = '数字とアイテムは同時に使えません。', 'error'
        elif guess_str:
            is_valid, err = is_valid_number(guess_str)
            if is_valid:
                guess = list(map(int, guess_str))
                eat, bite = judge(session['computer_number'], guess)
                session['history'].append(f"{session['turn']}. {guess_str} → {eat}-{bite}")
                session['turn'] += 1
                session['item_used_this_turn'] = False
                msg = f"{eat}EAT {bite}BITE"
                msg_type = 'success' if eat == 3 else 'info'
            else:
                msg, msg_type = err, 'error'
        elif item:
            if session['item_used_this_turn']:
                msg, msg_type = 'このターンでは既にアイテムを使用しました。', 'error'
            else:
                result = use_item(item, session['computer_number'])
                session['history'].append(result['effect'])
                session['item_used_this_turn'] = True
                session['used_items'].append(item)
                msg, msg_type = result['effect'], 'info'
        session.modified = True

    return render_template('game.html',
                           turn=session.get('turn'),
                           history=session.get('history'),
                           message=msg,
                           message_type=msg_type)

@app.route('/use-item', methods=['POST'])
def use_item_api():
    data = request.get_json()
    item_name = data.get('item_name')
    computer_number = session.get('computer_number')
    if not computer_number:
        return jsonify({'error': 'ゲームセッションが存在しません'}), 400

    result = use_item(item_name, computer_number)
    session['history'].append(result['effect'])
    session.modified = True
    app.logger.info(f"Item used: {item_name}, Result: {result['effect']}")
    return jsonify(result)

# ----------------------------------------
# サーバ起動
# ----------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=3000)