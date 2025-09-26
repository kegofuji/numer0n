#!/usr/bin/env python3
"""
数字当てゲームのデモンストレーション
自動でゲームを実行して動作を確認する
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from numeron_game import NumeronGame, GameMode, HumanPlayer, AIPlayer

def demo_single_player():
    """1人用ゲームのデモ"""
    print("🎮 1人用ゲームデモ 🎮")
    print("="*50)
    
    game = NumeronGame(GameMode.SINGLE_PLAYER)
    game.initialize_players()
    
    # プレイヤーの番号を設定
    game.player1.set_number([1, 2, 3])
    game.player2.set_number([4, 5, 6])
    
    print(f"プレイヤーの番号: {game.player1.number}")
    print(f"AIの番号: {game.player2.number}")
    print()
    
    # 数ターン実行
    for turn in range(3):
        print(f"--- ターン {turn + 1} ---")
        
        # プレイヤーのターン
        if turn == 0:
            # アイテム使用デモ
            item = game.player1.items[0]  # DOUBLE
            item.use()
            game.player1.used_items_this_turn = True
            result = game.process_item_effect(game.player1, item, game.player2)
            print(f"アイテム使用: {item.name}")
            print(f"効果: {result['effect']}")
            print()
        
        # コール
        guess = [1, 2, 4] if turn == 0 else [4, 5, 6] if turn == 1 else [4, 5, 7]
        eat, bite = game.calculate_eat_bite(game.player2.number, guess)
        game.player1.add_call_to_history(guess, eat, bite)
        game.player1.update_memo_cards(guess)
        
        print(f"プレイヤーの推測: {guess} → {eat}EAT {bite}BITE")
        
        if eat == 3:
            print("🎉 プレイヤーの勝利！")
            break
        
        # AIのターン
        ai_guess = game.player2.make_guess(game.player1)
        eat, bite = game.calculate_eat_bite(game.player1.number, ai_guess)
        game.player2.add_call_to_history(ai_guess, eat, bite)
        game.player2.update_possible_numbers(ai_guess, eat, bite)
        
        print(f"AIの推測: {ai_guess} → {eat}EAT {bite}BITE")
        
        if eat == 3:
            print("🎉 AIの勝利！")
            break
        
        print()

def demo_two_player():
    """2人用ゲームのデモ"""
    print("🎮 2人用ゲームデモ 🎮")
    print("="*50)
    
    game = NumeronGame(GameMode.TWO_PLAYER)
    game.initialize_players()
    
    # プレイヤーの番号を設定
    game.player1.set_number([7, 8, 9])
    game.player2.set_number([1, 2, 3])
    
    print(f"プレイヤー1の番号: {game.player1.number}")
    print(f"プレイヤー2の番号: {game.player2.number}")
    print()
    
    # 数ターン実行
    for turn in range(2):
        print(f"--- ターン {turn + 1} ---")
        
        # プレイヤー1のターン
        guess1 = [1, 2, 4] if turn == 0 else [1, 2, 3]
        eat, bite = game.calculate_eat_bite(game.player2.number, guess1)
        game.player1.add_call_to_history(guess1, eat, bite)
        
        print(f"プレイヤー1の推測: {guess1} → {eat}EAT {bite}BITE")
        
        if eat == 3:
            print("🎉 プレイヤー1の勝利！")
            break
        
        # プレイヤー2のターン
        guess2 = [7, 8, 0] if turn == 0 else [7, 8, 9]
        eat, bite = game.calculate_eat_bite(game.player1.number, guess2)
        game.player2.add_call_to_history(guess2, eat, bite)
        
        print(f"プレイヤー2の推測: {guess2} → {eat}EAT {bite}BITE")
        
        if eat == 3:
            print("🎉 プレイヤー2の勝利！")
            break
        
        print()

def demo_items():
    """アイテム効果のデモ"""
    print("🎮 アイテム効果デモ 🎮")
    print("="*50)
    
    game = NumeronGame(GameMode.SINGLE_PLAYER)
    game.initialize_players()
    game.player1.set_number([1, 2, 3])
    game.player2.set_number([4, 5, 6])
    
    print("全てのアイテム効果をデモンストレーションします:")
    print()
    
    for item in game.player1.items:
        print(f"--- {item.name}アイテム ---")
        result = game.process_item_effect(game.player1, item, game.player2)
        print(f"効果: {result['effect']}")
        print()

def main():
    """メインデモ関数"""
    print("🎮 数字当てゲーム デモンストレーション 🎮")
    print("="*60)
    
    try:
        demo_single_player()
        print("\n" + "="*60 + "\n")
        
        demo_two_player()
        print("\n" + "="*60 + "\n")
        
        demo_items()
        
        print("🎉 デモンストレーション完了！")
        print("実際のゲームをプレイするには 'python3 numeron_game.py' を実行してください。")
        
    except Exception as e:
        print(f"❌ デモ中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
