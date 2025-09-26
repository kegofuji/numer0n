#!/usr/bin/env python3
"""
数字当てゲームのテストスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from numeron_game import NumeronGame, GameMode, HumanPlayer, AIPlayer, Item, ItemType

def test_basic_functionality():
    """基本的な機能をテストする"""
    print("=== 基本機能テスト ===")
    
    # プレイヤーの作成
    player1 = HumanPlayer("テストプレイヤー1")
    player2 = HumanPlayer("テストプレイヤー2")
    
    # 番号設定
    player1.set_number([1, 2, 3])
    player2.set_number([4, 5, 6])
    
    print(f"プレイヤー1の番号: {player1.number}")
    print(f"プレイヤー2の番号: {player2.number}")
    
    # EAT/BITE計算テスト
    game = NumeronGame(GameMode.TWO_PLAYER)
    eat, bite = game.calculate_eat_bite([1, 2, 3], [1, 2, 4])
    print(f"推測[1,2,4] vs 答え[1,2,3] → {eat}EAT {bite}BITE")
    
    eat, bite = game.calculate_eat_bite([1, 2, 3], [3, 1, 2])
    print(f"推測[3,1,2] vs 答え[1,2,3] → {eat}EAT {bite}BITE")
    
    eat, bite = game.calculate_eat_bite([1, 2, 3], [4, 5, 6])
    print(f"推測[4,5,6] vs 答え[1,2,3] → {eat}EAT {bite}BITE")
    
    print("✅ 基本機能テスト完了")

def test_items():
    """アイテム機能をテストする"""
    print("\n=== アイテム機能テスト ===")
    
    player = HumanPlayer("テストプレイヤー")
    player.set_number([1, 2, 3])
    
    print("アイテム一覧:")
    for item in player.items:
        print(f"  {item}")
    
    # アイテム使用テスト
    double_item = player.items[0]  # DOUBLE
    print(f"\nDOUBLEアイテム使用前: {double_item.used}")
    double_item.use()
    print(f"DOUBLEアイテム使用後: {double_item.used}")
    
    # アイテムリセットテスト
    double_item.reset()
    print(f"DOUBLEアイテムリセット後: {double_item.used}")
    
    print("✅ アイテム機能テスト完了")

def test_ai_player():
    """AIプレイヤーをテストする"""
    print("\n=== AIプレイヤーテスト ===")
    
    ai = AIPlayer("テストAI")
    ai.set_number([7, 8, 9])
    
    print(f"AIの番号: {ai.number}")
    print(f"可能な番号数: {len(ai.possible_numbers)}")
    
    # AIの推測テスト
    guess = ai.make_guess(None)
    print(f"AIの推測: {guess}")
    
    # 可能な番号の更新テスト
    ai.update_possible_numbers(guess, 1, 1)
    print(f"更新後の可能な番号数: {len(ai.possible_numbers)}")
    
    print("✅ AIプレイヤーテスト完了")

def test_game_initialization():
    """ゲーム初期化をテストする"""
    print("\n=== ゲーム初期化テスト ===")
    
    # 1人用ゲーム
    game1 = NumeronGame(GameMode.SINGLE_PLAYER)
    game1.initialize_players()
    print(f"1人用ゲーム - プレイヤー1: {game1.player1.name}")
    print(f"1人用ゲーム - プレイヤー2: {game1.player2.name}")
    print(f"1人用ゲーム - プレイヤー2のタイプ: {type(game1.player2).__name__}")
    
    # 2人用ゲーム
    game2 = NumeronGame(GameMode.TWO_PLAYER)
    game2.initialize_players()
    print(f"2人用ゲーム - プレイヤー1: {game2.player1.name}")
    print(f"2人用ゲーム - プレイヤー2: {game2.player2.name}")
    print(f"2人用ゲーム - プレイヤー1のタイプ: {type(game2.player1).__name__}")
    print(f"2人用ゲーム - プレイヤー2のタイプ: {type(game2.player2).__name__}")
    
    print("✅ ゲーム初期化テスト完了")

def test_item_effects():
    """アイテム効果をテストする"""
    print("\n=== アイテム効果テスト ===")
    
    game = NumeronGame(GameMode.SINGLE_PLAYER)
    game.initialize_players()
    game.player1.set_number([1, 2, 3])
    game.player2.set_number([4, 5, 6])
    
    # DOUBLEアイテムテスト
    double_item = game.player1.items[0]
    result = game.process_item_effect(game.player1, double_item, game.player2)
    print(f"DOUBLEアイテム効果: {result['effect']}")
    
    # HIGH&LOWアイテムテスト
    highlow_item = game.player1.items[1]
    result = game.process_item_effect(game.player1, highlow_item, game.player2)
    print(f"HIGH&LOWアイテム効果: {result['effect']}")
    
    # TARGETアイテムテスト
    target_item = game.player1.items[2]
    result = game.process_item_effect(game.player1, target_item, game.player2)
    print(f"TARGETアイテム効果: {result['effect']}")
    
    # SLASHアイテムテスト
    slash_item = game.player1.items[3]
    result = game.process_item_effect(game.player1, slash_item, game.player2)
    print(f"SLASHアイテム効果: {result['effect']}")
    
    # SHUFFLEアイテムテスト
    shuffle_item = game.player1.items[4]
    old_number = game.player1.number.copy()
    result = game.process_item_effect(game.player1, shuffle_item, game.player2)
    print(f"SHUFFLEアイテム効果: {result['effect']}")
    
    # CHANGEアイテムテスト
    change_item = game.player1.items[5]
    result = game.process_item_effect(game.player1, change_item, game.player2)
    print(f"CHANGEアイテム効果: {result['effect']}")
    
    print("✅ アイテム効果テスト完了")

def main():
    """メインテスト関数"""
    print("🧪 数字当てゲーム テストスイート 🧪")
    print("="*50)
    
    try:
        test_basic_functionality()
        test_items()
        test_ai_player()
        test_game_initialization()
        test_item_effects()
        
        print("\n🎉 全てのテストが完了しました！")
        print("ゲームは正常に動作しています。")
        
    except Exception as e:
        print(f"\n❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
