import os
import logging
from datetime import datetime
from flask import Flask, request, render_template, session, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
from config import config
import random

# 環境変数の読み込み
load_dotenv()

def create_app(config_name=None):
    """アプリケーションファクトリ"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__, template_folder='../frontend/templates')
    app.config.from_object(config[config_name])
    
    # ログ設定
    setup_logging(app)
    
    return app

def setup_logging(app):
    """ログ設定"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
        handlers=[
            logging.FileHandler(app.config['LOG_FILE']),
            logging.StreamHandler()
        ]
    )

app = create_app()

# 3桁ユニークな数字を生成（コンピュータ用）
def generate_computer_number():
    digits = list(range(10))
    random.shuffle(digits)
    # 先頭が0にならないように
    if digits[0] == 0:
        for i in range(1, 10):
            if digits[i] != 0:
                digits[0], digits[i] = digits[i], digits[0]
                break
    return digits[:3]

# EAT/BITE判定
def judge(answer, guess):
    """
    Numeronの正しい判定ロジック
    EAT: 同じ位置で同じ数字
    BITE: 数字は含まれるが位置が違う（重複は考慮しない）
    """
    eat = 0
    bite = 0
    
    # EATの計算（同じ位置で同じ数字）
    for a, g in zip(answer, guess):
        if a == g:
            eat += 1
    
    # BITEの計算（数字は含まれるが位置が違う）
    for i, g in enumerate(guess):
        if g in answer and answer[i] != g:
            bite += 1
    
    return eat, bite

# 数字の妥当性チェック（強化版）
def is_valid_number(number_str):
    if len(number_str) != 3 or not number_str.isdigit():
        return False, "3桁の数字を入力してください"
    if len(set(number_str)) != 3:
        return False, "数字の重複は禁止です"
    return True, ""

# アイテム機能
def use_item(item_name, computer_number, player_number=None, target_digit=None, position=None, group=None):
    """アイテム効果を実行"""
    if item_name == 'DOUBLE':
        # 1桁をランダムに開示
        reveal_pos = random.randint(0, 2)
        reveal_digit = computer_number[reveal_pos]
        position_names = ['百の位', '十の位', '一の位']
        return {
            'effect': f"DOUBLE効果: {position_names[reveal_pos]}の数字は{reveal_digit}です",
            'reveal_pos': reveal_pos,
            'reveal_digit': reveal_digit,
            'double_call': True  # 2回連続コール可能フラグ
        }
    
    elif item_name == 'HIGH_LOW':
        # HIGH(5-9)とLOW(0-4)の位置を教える
        position_names = ['百の位', '十の位', '一の位']
        high_positions = [position_names[i] for i, d in enumerate(computer_number) if d >= 5]
        low_positions = [position_names[i] for i, d in enumerate(computer_number) if d < 5]
        return {
            'effect': f"HIGH_LOW効果: HIGH(5-9)は{high_positions}、LOW(0-4)は{low_positions}",
            'high_positions': high_positions,
            'low_positions': low_positions
        }
    
    elif item_name == 'TARGET':
        # 指定数字の存在確認
        if target_digit is None:
            return {'error': 'TARGETアイテムには数字の指定が必要です'}
        
        position_names = ['百の位', '十の位', '一の位']
        positions = [position_names[i] for i, d in enumerate(computer_number) if d == target_digit]
        if positions:
            return {
                'effect': f"TARGET効果: 数字{target_digit}は{positions}に含まれています",
                'found': True,
                'positions': positions
            }
        else:
            return {
                'effect': f"TARGET効果: 数字{target_digit}は含まれていません",
                'found': False
            }
    
    elif item_name == 'SLASH':
        # 最大値-最小値
        max_val = max(computer_number)
        min_val = min(computer_number)
        diff = max_val - min_val
        return {
            'effect': f"SLASH効果: 最大値{max_val} - 最小値{min_val} = {diff}",
            'max_val': max_val,
            'min_val': min_val,
            'difference': diff
        }
    
    return {'effect': "アイテム効果が実行されました"}

def log_game_result(session_data):
    """ゲーム結果をログに記録"""
    try:
        winner = session_data.get('winner')
        turn = session_data.get('turn', 1)
        history = session_data.get('history', [])
        
        app.logger.info(f"Game finished - Winner: {winner}, Turns: {turn-1}, Moves: {len(history)}")
        
        # 詳細な手番履歴をログに記録
        for move in history:
            app.logger.info(f"Move: {move}")
            
    except Exception as e:
        app.logger.error(f"Failed to log game result: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    # セッション初期化（新しいゲームの場合のみ）
    if 'game_state' not in session or 'computer_number' not in session or request.args.get('new_game') == 'true':
        session.clear()  # セッションをクリア
        session['game_state'] = 'playing'  # playing, finished
        session['turn'] = 1
        session['computer_number'] = generate_computer_number()
        session['history'] = []
        session['winner'] = None
        session['start_time'] = datetime.utcnow().isoformat()
        app.logger.info(f"New game started with computer number: {session['computer_number']}")
    
    game_state = session['game_state']
    turn = session['turn']
    message = ''
    message_type = 'info'
    
    if game_state == 'playing':
        # 対戦フェーズ
    if request.method == 'POST':
        guess_str = request.form.get('guess', '')
            used_items = request.form.getlist('used_items')  # 使用したアイテムのリスト
            target_digit = request.form.get('target_digit')
            
            if guess_str:
                is_valid, error_msg = is_valid_number(guess_str)
                if is_valid:
            guess = [int(d) for d in guess_str]
                    
                    # プレイヤーの数字をセッションに保存
                    session['player_number'] = guess.copy()
                    
                    # アイテム効果を適用
                    item_results = []
                    for item_name in used_items:
                        if item_name:
                            # アイテム固有のパラメータを設定
                            item_target_digit = int(target_digit) if item_name == 'TARGET' and target_digit else None
                            
                            item_result = use_item(item_name, session['computer_number'], guess, 
                                                 item_target_digit, None, None)
                            if 'error' not in item_result:
                                item_results.append(item_result['effect'])
                                # 特殊効果の処理
                                if 'new_number' in item_result:
                                    session['player_number'] = item_result['new_number']
                                if 'double_call' in item_result:
                                    session['double_call_available'] = True
                    
                    # DOUBLEコール使用後はフラグをリセット
                    if session.get('double_call_available', False):
                        session['double_call_available'] = False
                    
                    # コンピュータの数字と比較
                    computer_number = session['computer_number']
                    eat, bite = judge(computer_number, guess)
                    
                    # 履歴に追加（アイテム効果も含める）
                    result = f'{len(session["history"]) + 1}. {guess_str} → {eat}-{bite}'
                    if item_results:
                        result += f' (アイテム: {", ".join(item_results)})'
                    session['history'].append(result)
                    
                    # セッションを確実に保存
                    session.modified = True
                    
                    app.logger.info(f"Player guessed {guess_str}: {eat}EAT, {bite}BITE")
                    app.logger.info(f"Items used: {used_items}")
                    app.logger.info(f"Current history: {session['history']}")
                    
                    # 勝敗判定
            if eat == 3:
                        session['winner'] = 'player'
                        session['game_state'] = 'finished'
                        session['end_time'] = datetime.utcnow().isoformat()
                        message = f'🎉 おめでとうございます！{turn}ターンで正解です！'
                        message_type = 'success'
                        log_game_result(session)
                    else:
                        # 次のターン
                        session['turn'] += 1
                        message = f'次の数字を入力してください'
                        message_type = 'info'
                else:
                    message = error_msg
                    message_type = 'error'
                    app.logger.warning(f"Invalid guess input: {guess_str} - {error_msg}")
        else:
            # GETリクエスト時は新しい数字を生成して履歴をクリア
            session['computer_number'] = generate_computer_number()
            session['history'] = []
            session['turn'] = 1
            session.modified = True
            app.logger.info(f"Page refreshed - New number generated: {session['computer_number']}")
        
        # デバッグ情報をログに出力
        app.logger.info(f"Rendering game page - History length: {len(session.get('history', []))}")
        app.logger.info(f"History content: {session.get('history', [])}")
        
        return render_template('game.html', 
                             turn=turn,
                             history=session.get('history', []),
                             message=message,
                             message_type=message_type)
    
    else:  # finished
        # 結果表示
        if request.method == 'POST':
            # 新しいゲーム開始
            return redirect(url_for('index', new_game='true'))
        
        return render_template('result.html',
                             winner=session['winner'],
                             history=session['history'],
                             turn=session.get('turn', 1))

@app.route('/new-game')
def new_game():
    """新しいゲームを開始"""
    session.clear()  # セッションを完全にクリア
    session['game_state'] = 'playing'
    session['turn'] = 1
    session['computer_number'] = generate_computer_number()  # 新しい数字を生成
    session['history'] = []
    session['winner'] = None
    session['start_time'] = datetime.utcnow().isoformat()
    app.logger.info(f"New game started with computer number: {session['computer_number']}")
    return redirect(url_for('index'))

@app.route('/use-item', methods=['POST'])
def use_item_endpoint():
    """アイテム使用エンドポイント"""
    try:
        data = request.get_json()
        item_name = data.get('item')
        target_digit = data.get('target_digit')
        position = data.get('position')
        group = data.get('group')
        
        if not item_name:
            return jsonify({'error': 'アイテム名が指定されていません'}), 400
        
        computer_number = session.get('computer_number')
        if not computer_number:
            return jsonify({'error': 'ゲームが開始されていません'}), 400
        
        # プレイヤーの数字を取得（セッションから）
        player_number = session.get('player_number')
        
        # アイテム効果を実行
        result = use_item(item_name, computer_number, player_number, target_digit, position, group)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        # 結果をセッションに保存
        if 'new_number' in result:
            session['player_number'] = result['new_number']
        if 'double_call' in result:
            session['double_call_available'] = True
        
        app.logger.info(f"Item {item_name} used: {result}")
        
        return jsonify({
            'success': True,
            'result': result,
            'item': item_name
        })
        
    except Exception as e:
        app.logger.error(f"Error using item: {e}")
        return jsonify({'error': 'アイテム使用中にエラーが発生しました'}), 500

@app.route('/check-double-call')
def check_double_call():
    """DOUBLEコール可能状態をチェック"""
    double_call_available = session.get('double_call_available', False)
    return jsonify({
        'double_call_available': double_call_available
    })

@app.route('/stats')
def stats():
    """統計ページ（簡易版）"""
    try:
        # 現在はセッションから統計を取得
        return render_template('stats.html', 
                             message="統計機能は準備中です。データベース連携後に実装予定。")
    except Exception as e:
        app.logger.error(f"Error loading stats: {e}")
        return render_template('stats.html', error="統計情報の読み込みに失敗しました")

if __name__ == '__main__':
    app.run(debug=True, port=3000) 