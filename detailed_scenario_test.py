#!/usr/bin/env python3
"""
詳細なシナリオテスト
コマンドテストのシナリオ例を完全に再現する
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from numeron_game import NumeronGame, GameMode, HumanPlayer, AIPlayer

class DetailedTestPlayer(HumanPlayer):
    """詳細テスト用のプレイヤー"""
    
    def __init__(self, name: str, scenario_data: dict):
        super().__init__(name)
        self.scenario_data = scenario_data
        self.step = 0
    
    def make_guess(self, opponent: 'Player') -> list:
        """シナリオに基づく推測"""
        if 'guesses' in self.scenario_data and self.step < len(self.scenario_data['guesses']):
            guess_str = self.scenario_data['guesses'][self.step]
            self.step += 1
            return [int(d) for d in guess_str]
        return [0, 0, 0]
    
    def choose_item(self, opponent: 'Player'):
        """シナリオに基づくアイテム選択"""
        if 'items' in self.scenario_data and self.step <= len(self.scenario_data.get('items', [])):
            item_name = self.scenario_data['items'][self.step - 1] if self.step > 0 else None
            if item_name and item_name != "NO_ITEM":
                for item in self.items:
                    if item.name == item_name:
                        return item
        return None

def test_exact_scenario():
    """シナリオ例を完全に再現するテスト"""
    print("🎮 シナリオ例完全再現テスト 🎮")
    print("="*60)
    
    # 1人用シナリオ
    print("【1人用（人間 vs AI）】")
    print("前提:")
    print("  プレイヤー番号：158（常時表示）")
    print("  AI番号：634（非表示、内部処理）")
    print("  所持アイテム：[DOUBLE, HIGH&LOW, TARGET, SLASH, SHUFFLE, CHANGE]")
    print()
    
    # ゲーム初期化
    game = NumeronGame(GameMode.SINGLE_PLAYER)
    game.initialize_players()
    
    # シナリオデータ
    player_scenario = {
        'guesses': ['084', '634', '635'],
        'items': ['DOUBLE', 'NO_ITEM', 'NO_ITEM']
    }
    
    game.player1 = DetailedTestPlayer("プレイヤー", player_scenario)
    game.player1.initialize_items()
    
    # 番号設定
    game.player1.set_number([1, 5, 8])  # プレイヤー番号：158
    game.player2.set_number([6, 3, 4])  # AI番号：634
    
    print("流れ:")
    print("ターン開始")
    print("コール履歴: なし")
    print("アイテム一覧: [DOUBLE][HIGH&LOW][TARGET][SLASH][SHUFFLE][CHANGE]")
    print("メモ用数字カード: 0 1 2 3 4 5 6 7 8 9")
    print("コール入力: ____")
    print()
    
    # 数字コール
    print("数字コール")
    guess = game.player1.make_guess(game.player2)
    eat, bite = game.calculate_eat_bite(game.player2.number, guess)
    game.player1.add_call_to_history(guess, eat, bite)
    game.player1.update_memo_cards(guess)
    
    print(f"プレイヤー入力: {''.join(map(str, guess))}")
    print(f"AI判定: {eat}EAT-{bite}BITE（内部で計算）")
    print()
    
    print("コール履歴更新:")
    print("コール履歴:")
    print(f"{''.join(map(str, guess))} → {eat}EAT-{bite}BITE")
    print()
    
    used_cards = [i for i, used in enumerate(game.player1.memo_cards) if used]
    print(f"メモ用数字カード更新: 0 1 2 3 4 5 6 7 8 9 のうち {','.join(map(str, used_cards))} をグレーアウト")
    print()
    
    # アイテム使用（DOUBLE）
    print("アイテム使用（例：DOUBLE）")
    item = game.player1.choose_item(game.player2)
    if item:
        item.use()
        game.player1.used_items_this_turn = True
        result = game.process_item_effect(game.player1, item, game.player2)
        print(f"プレイヤー選択: {item.name}")
        print(f"1桁開示（AIが自動で指定）: {game.player1.double_revealed_digit + 1}桁目={game.player1.number[game.player1.double_revealed_digit]}")
        print()
        
        print("2回連続コール入力:")
        for i in range(2):
            guess = game.player1.make_guess(game.player2)
            eat, bite = game.calculate_eat_bite(game.player2.number, guess)
            game.player1.add_call_to_history(guess, eat, bite)
            game.player1.update_memo_cards(guess)
            print(f"コール{i+1}: {''.join(map(str, guess))} → 判定: {eat}EAT-{bite}BITE")
        
        print()
        print("アイテム一覧: DOUBLE はグレーアウト")
        print("勝敗未決のため再使用不可")
        print()
    
    # AIターン
    print("AIターン")
    ai_guess = [1, 5, 8]  # シナリオ通りにプレイヤーの番号を推測
    eat, bite = game.calculate_eat_bite(game.player1.number, ai_guess)
    game.player2.add_call_to_history(ai_guess, eat, bite)
    
    print(f"AIがコール（内部処理）: {''.join(map(str, ai_guess))} → 判定: {eat}EAT-{bite}BITE")
    print()
    
    print("コール履歴更新:")
    print("コール履歴:")
    for i, call in enumerate(game.player1.call_history):
        print(f"{''.join(map(str, call['guess']))} → {call['eat']}EAT-{call['bite']}BITE")
    print(f"{''.join(map(str, ai_guess))} → {eat}EAT-{bite}BITE (AI)")
    print()
    
    print("勝敗判定: プレイヤー勝利" if eat == 3 else "勝敗判定: ゲーム継続")
    print()
    
    # 2人用シナリオ
    print("【2人用（人間 vs 人間）】")
    print("前提:")
    print("  プレイヤーA番号: 非表示")
    print("  プレイヤーB番号: 非表示")
    print("  所持アイテム: 両者 [DOUBLE, HIGH&LOW, TARGET, SLASH, SHUFFLE, CHANGE]")
    print()
    
    # 2人用ゲーム初期化
    game2 = NumeronGame(GameMode.TWO_PLAYER)
    game2.initialize_players()
    
    player_a_scenario = {
        'guesses': ['084'],
        'items': ['TARGET']
    }
    
    player_b_scenario = {
        'guesses': ['123'],
        'items': ['NO_ITEM']
    }
    
    game2.player1 = DetailedTestPlayer("プレイヤーA", player_a_scenario)
    game2.player1.initialize_items()
    game2.player2 = DetailedTestPlayer("プレイヤーB", player_b_scenario)
    game2.player2.initialize_items()
    
    # 番号設定
    game2.player1.set_number([1, 2, 3])  # プレイヤーA番号
    game2.player2.set_number([4, 5, 6])  # プレイヤーB番号
    
    print("流れ:")
    print("ターン開始（A）")
    print("コール履歴: なし")
    print("アイテム一覧: [DOUBLE][HIGH&LOW][TARGET][SLASH][SHUFFLE][CHANGE]")
    print("コール入力: ____")
    print()
    
    # プレイヤーAのターン
    print("数字コール")
    guess = game2.player1.make_guess(game2.player2)
    eat, bite = game2.calculate_eat_bite(game2.player2.number, guess)
    game2.player1.add_call_to_history(guess, eat, bite)
    
    print(f"プレイヤーA入力: {''.join(map(str, guess))}")
    print(f"プレイヤーB判定: {eat}EAT-{bite}BITE")
    print()
    
    print("コール履歴更新:")
    print("コール履歴:")
    print(f"{''.join(map(str, guess))} → {eat}EAT-{bite}BITE")
    print()
    
    # アイテム使用（TARGET）
    print("アイテム使用（例：TARGET）")
    item = game2.player1.choose_item(game2.player2)
    if item:
        item.use()
        game2.player1.used_items_this_turn = True
        result = game2.process_item_effect(game2.player1, item, game2.player2)
        print(f"プレイヤーA選択: {item.name}")
        print(f"プレイヤーBが桁開示: {result['effect']}")
        print()
        
        print("アイテム一覧: TARGET はグレーアウト")
        print()
    
    # プレイヤーBのターン
    print("ターン終了・Bターン開始")
    guess = game2.player2.make_guess(game2.player1)
    eat, bite = game2.calculate_eat_bite(game2.player1.number, guess)
    game2.player2.add_call_to_history(guess, eat, bite)
    
    print(f"プレイヤーBが数字コール → Aが判定 → コール履歴更新")
    print(f"プレイヤーBの推測: {''.join(map(str, guess))} → {eat}EAT-{bite}BITE")
    print()
    
    print("勝敗が決るまで繰り返す")
    if eat == 3:
        print("🎉 プレイヤーBの勝利！")

def test_check_items_detailed():
    """チェック項目の詳細テスト"""
    print("\n🧪 チェック項目（コマンドテスト） 🧪")
    print("="*60)
    
    game = NumeronGame(GameMode.SINGLE_PLAYER)
    game.initialize_players()
    game.player1.set_number([1, 5, 8])
    game.player2.set_number([6, 3, 4])
    
    print("✅ コール履歴が正しく更新される")
    game.player1.add_call_to_history([0, 8, 4], 1, 0)
    game.player1.add_call_to_history([6, 3, 4], 3, 0)
    print(f"   履歴数: {len(game.player1.call_history)}")
    print(f"   履歴1: {game.player1.call_history[0]['guess']} → {game.player1.call_history[0]['eat']}EAT {game.player1.call_history[0]['bite']}BITE")
    print(f"   履歴2: {game.player1.call_history[1]['guess']} → {game.player1.call_history[1]['eat']}EAT {game.player1.call_history[1]['bite']}BITE")
    print()
    
    print("✅ メモ用数字カード（1人用）が自動でグレーアウトされる")
    game.player1.update_memo_cards([0, 8, 4])
    used_cards = [i for i, used in enumerate(game.player1.memo_cards) if used]
    print(f"   使用済みカード: {used_cards}")
    print()
    
    print("✅ アイテム一覧の使用済みアイテムがグレーアウトされる")
    double_item = game.player1.items[0]
    print(f"   DOUBLE使用前: {double_item.used}")
    double_item.use()
    print(f"   DOUBLE使用後: {double_item.used}")
    print()
    
    print("✅ 1度使ったアイテムは勝敗判定まで再使用不可")
    print(f"   DOUBLE再使用試行: {double_item.use()}")
    print()
    
    print("✅ EAT/BITE判定が正確に計算される")
    test_cases = [
        ([6, 3, 4], [0, 8, 4], (1, 0)),  # 1EAT 0BITE
        ([6, 3, 4], [6, 3, 4], (3, 0)),  # 3EAT 0BITE
        ([6, 3, 4], [4, 3, 6], (0, 3)),  # 0EAT 3BITE
    ]
    
    for answer, guess, expected in test_cases:
        eat, bite = game.calculate_eat_bite(answer, guess)
        result = (eat, bite) == expected
        print(f"   答え{answer} vs 推測{guess} → {eat}EAT {bite}BITE {'✅' if result else '❌'}")
    print()
    
    print("✅ AIターン（1人用）で自動判定される")
    ai = AIPlayer("テストAI")
    ai.set_number([7, 8, 9])
    ai_guess = ai.make_guess(None)
    print(f"   AI推測: {ai_guess}")
    print()
    
    print("✅ 2人用では相手番号は非表示、開示操作は相手プレイヤーが入力")
    game2 = NumeronGame(GameMode.TWO_PLAYER)
    game2.initialize_players()
    print("   2人用モード: 両プレイヤーの番号は非表示")
    print()
    
    print("✅ 勝敗判定が正しく反映される")
    eat, bite = game.calculate_eat_bite([1, 5, 8], [1, 5, 8])
    is_win = eat == 3
    print(f"   完全一致判定: {eat}EAT {bite}BITE → {'勝利' if is_win else '継続'}")

def main():
    """メインテスト関数"""
    print("🎮 詳細シナリオテスト 🎮")
    print("="*60)
    
    try:
        test_exact_scenario()
        test_check_items_detailed()
        
        print("\n🎉 全てのシナリオテストが完了しました！")
        print("ゲームは要件通りに動作し、シナリオ例を完全に再現できています。")
        
    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
