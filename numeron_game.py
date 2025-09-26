#!/usr/bin/env python3
"""
数字当てゲーム（3桁戦）＋アイテム付き
Numeron Game with Items

【ゲーム概要】
- プレイヤーは0〜9の数字カードから重複なしで3桁の番号を設定
- 先攻・後攻交互に相手の番号を推測
- 推測結果は EAT（数字+桁一致）・BITE（数字のみ一致）で表示
- 先に相手の番号を完全に当てたプレイヤーが勝利
- 入力は数字入力のみ

【対戦形式】
- 1人用（人間 vs AI）と2人用（人間 vs 人間）を実装
- 1人用はAIの番号非表示、メモ用数字カードで自分のコールや判明数字をグレーアウト表示
- 2人用は互いの番号非表示

【アイテム仕様】
- アイテム種類（全6個）
  1. 攻撃系
     - DOUBLE（黄）：2回連続コール可能。ただし1桁開示。2回目のコール時はアイテム使用不可。
     - HIGH&LOW（青&赤）：相手番号の各桁がHIGH(5-9)/LOW(0-4)か判明。第3回ではHIGH/LOWの数字数。
     - TARGET（紫）：指定数字が相手番号に含まれるか確認。含まれる場合は桁も判明。
     - SLASH（エメラルドグリーン）：最大数-最小数（スラッシュナンバー）を取得。
  2. 防御系
     - SHUFFLE（緑）：自分の番号を並べ替え可能。
     - CHANGE（桃）：自分の番号の1桁を手持ちカードと交換可能（HIGH/LOW保持）。
"""

import random
import os
import sys
from typing import List, Tuple, Optional, Dict, Any
from abc import ABC, abstractmethod
from enum import Enum


class GameMode(Enum):
    """ゲームモード"""
    SINGLE_PLAYER = "1人用"
    TWO_PLAYER = "2人用"


class ItemType(Enum):
    """アイテムタイプ"""
    ATTACK = "攻撃系"
    DEFENSE = "防御系"


class Item:
    """アイテムクラス"""
    
    def __init__(self, name: str, item_type: ItemType, color: str, description: str):
        self.name = name
        self.item_type = item_type
        self.color = color
        self.description = description
        self.used = False
    
    def use(self) -> bool:
        """アイテムを使用する"""
        if self.used:
            return False
        self.used = True
        return True
    
    def reset(self):
        """アイテムをリセットする"""
        self.used = False
    
    def __str__(self):
        status = "使用済み" if self.used else "使用可能"
        return f"{self.name} ({self.color}) - {status}"


class Player(ABC):
    """プレイヤークラス（抽象クラス）"""
    
    def __init__(self, name: str):
        self.name = name
        self.number: List[int] = []
        self.items: List[Item] = []
        self.call_history: List[Dict[str, Any]] = []
        self.memo_cards: List[bool] = [False] * 10  # 0-9の数字カードの使用状況
        self.known_digits: List[Optional[int]] = [None, None, None]  # 判明した数字
        self.used_items_this_turn = False
        self.double_call_count = 0  # DOUBLEアイテム使用時の連続コール回数
        self.double_revealed_digit = None  # DOUBLEアイテムで開示された桁
    
    def set_number(self, number: List[int]):
        """番号を設定する"""
        if len(number) != 3 or len(set(number)) != 3:
            raise ValueError("3桁の重複なしの数字を入力してください")
        self.number = number.copy()
    
    def generate_random_number(self) -> List[int]:
        """ランダムな番号を生成する"""
        digits = list(range(10))
        random.shuffle(digits)
        # 最初の桁が0でないようにする
        if digits[0] == 0:
            for i in range(1, 10):
                if digits[i] != 0:
                    digits[0], digits[i] = digits[i], digits[0]
                    break
        return digits[:3]
    
    def add_call_to_history(self, guess: List[int], eat: int, bite: int, item_used: str = None):
        """コール履歴に追加する"""
        self.call_history.append({
            'guess': guess.copy(),
            'eat': eat,
            'bite': bite,
            'item_used': item_used
        })
    
    def update_memo_cards(self, guess: List[int]):
        """メモ用数字カードを更新する"""
        for digit in guess:
            self.memo_cards[digit] = True
    
    def can_use_item(self) -> bool:
        """アイテムを使用できるかチェックする"""
        return not self.used_items_this_turn
    
    def reset_turn(self):
        """ターンをリセットする"""
        self.used_items_this_turn = False
        self.double_call_count = 0
        self.double_revealed_digit = None
    
    @abstractmethod
    def make_guess(self, opponent: 'Player') -> List[int]:
        """推測を行う（抽象メソッド）"""
        pass
    
    @abstractmethod
    def choose_item(self, opponent: 'Player') -> Optional[Item]:
        """アイテムを選択する（抽象メソッド）"""
        pass


class HumanPlayer(Player):
    """人間プレイヤークラス"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.initialize_items()
    
    def initialize_items(self):
        """アイテムを初期化する"""
        self.items = [
            Item("DOUBLE", ItemType.ATTACK, "黄", "2回連続コール可能。ただし1桁開示。"),
            Item("HIGH&LOW", ItemType.ATTACK, "青&赤", "相手番号の各桁がHIGH(5-9)/LOW(0-4)か判明。"),
            Item("TARGET", ItemType.ATTACK, "紫", "指定数字が相手番号に含まれるか確認。"),
            Item("SLASH", ItemType.ATTACK, "エメラルドグリーン", "最大数-最小数（スラッシュナンバー）を取得。"),
            Item("SHUFFLE", ItemType.DEFENSE, "緑", "自分の番号を並べ替え可能。"),
            Item("CHANGE", ItemType.DEFENSE, "桃", "自分の番号の1桁を手持ちカードと交換可能。")
        ]
    
    def make_guess(self, opponent: 'Player') -> List[int]:
        """推測を行う"""
        while True:
            try:
                guess_input = input(f"{self.name}の推測（3桁の数字）: ").strip()
                if len(guess_input) != 3 or not guess_input.isdigit():
                    print("3桁の数字を入力してください")
                    continue
                
                guess = [int(d) for d in guess_input]
                if len(set(guess)) != 3:
                    print("数字の重複は禁止です")
                    continue
                
                return guess
            except (ValueError, KeyboardInterrupt):
                print("正しい形式で入力してください")
                continue
    
    def choose_item(self, opponent: 'Player') -> Optional[Item]:
        """アイテムを選択する"""
        if not self.can_use_item():
            return None
        
        available_items = [item for item in self.items if not item.used]
        if not available_items:
            return None
        
        print(f"\n{self.name}のアイテム選択:")
        for i, item in enumerate(available_items, 1):
            print(f"{i}. {item}")
        
        print("0. アイテムを使用しない")
        
        while True:
            try:
                choice = input("選択してください (0-{}): ".format(len(available_items))).strip()
                if choice == "0":
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(available_items):
                    return available_items[choice_num - 1]
                else:
                    print("正しい番号を入力してください")
            except (ValueError, KeyboardInterrupt):
                print("正しい番号を入力してください")
                continue


class AIPlayer(Player):
    """AIプレイヤークラス"""
    
    def __init__(self, name: str = "AI"):
        super().__init__(name)
        self.initialize_items()
        self.possible_numbers = []
        self.generate_all_possible_numbers()
    
    def initialize_items(self):
        """アイテムを初期化する"""
        self.items = [
            Item("DOUBLE", ItemType.ATTACK, "黄", "2回連続コール可能。ただし1桁開示。"),
            Item("HIGH&LOW", ItemType.ATTACK, "青&赤", "相手番号の各桁がHIGH(5-9)/LOW(0-4)か判明。"),
            Item("TARGET", ItemType.ATTACK, "紫", "指定数字が相手番号に含まれるか確認。"),
            Item("SLASH", ItemType.ATTACK, "エメラルドグリーン", "最大数-最小数（スラッシュナンバー）を取得。"),
            Item("SHUFFLE", ItemType.DEFENSE, "緑", "自分の番号を並べ替え可能。"),
            Item("CHANGE", ItemType.DEFENSE, "桃", "自分の番号の1桁を手持ちカードと交換可能。")
        ]
    
    def generate_all_possible_numbers(self):
        """全ての可能な番号を生成する"""
        self.possible_numbers = []
        for i in range(1, 10):  # 最初の桁は1-9
            for j in range(10):
                if j != i:
                    for k in range(10):
                        if k != i and k != j:
                            self.possible_numbers.append([i, j, k])
    
    def make_guess(self, opponent: 'Player') -> List[int]:
        """推測を行う（AI戦略）"""
        if not self.possible_numbers:
            # フォールバック: ランダムな推測
            return self.generate_random_number()
        
        # 自分の番号を除外して推測
        filtered_numbers = [num for num in self.possible_numbers if num != self.number]
        if filtered_numbers:
            return random.choice(filtered_numbers)
        else:
            return random.choice(self.possible_numbers)
    
    def choose_item(self, opponent: 'Player') -> Optional[Item]:
        """アイテムを選択する（AI戦略）"""
        if not self.can_use_item():
            return None
        
        available_items = [item for item in self.items if not item.used]
        if not available_items:
            return None
        
        # 簡単なAI戦略: ランダムにアイテムを選択
        if random.random() < 0.3:  # 30%の確率でアイテムを使用
            return random.choice(available_items)
        
        return None
    
    def update_possible_numbers(self, guess: List[int], eat: int, bite: int):
        """可能な番号を更新する"""
        new_possible = []
        for number in self.possible_numbers:
            if self.calculate_eat_bite(number, guess) == (eat, bite):
                new_possible.append(number)
        self.possible_numbers = new_possible
    
    def calculate_eat_bite(self, answer: List[int], guess: List[int]) -> Tuple[int, int]:
        """EATとBITEを計算する"""
        eat = sum(a == g for a, g in zip(answer, guess))
        bite = sum(min(answer.count(d), guess.count(d)) for d in set(guess)) - eat
        return eat, bite


class NumeronGame:
    """数字当てゲームクラス"""
    
    def __init__(self, mode: GameMode):
        self.mode = mode
        self.player1: Player = None
        self.player2: Player = None
        self.current_player: Player = None
        self.turn_count = 0
        self.game_ended = False
        self.winner: Player = None
    
    def initialize_players(self):
        """プレイヤーを初期化する"""
        if self.mode == GameMode.SINGLE_PLAYER:
            self.player1 = HumanPlayer("プレイヤー")
            self.player2 = AIPlayer("AI")
        else:
            self.player1 = HumanPlayer("プレイヤー1")
            self.player2 = HumanPlayer("プレイヤー2")
        
        self.current_player = self.player1
    
    def setup_numbers(self):
        """番号を設定する"""
        print("\n=== 番号設定 ===")
        
        if self.mode == GameMode.SINGLE_PLAYER:
            # プレイヤーの番号設定
            while True:
                try:
                    player_input = input("プレイヤーの番号（3桁の数字）: ").strip()
                    if len(player_input) != 3 or not player_input.isdigit():
                        print("3桁の数字を入力してください")
                        continue
                    
                    player_number = [int(d) for d in player_input]
                    if len(set(player_number)) != 3:
                        print("数字の重複は禁止です")
                        continue
                    
                    self.player1.set_number(player_number)
                    break
                except (ValueError, KeyboardInterrupt):
                    print("正しい形式で入力してください")
                    continue
            
            # AIの番号は自動生成
            self.player2.set_number(self.player2.generate_random_number())
            print("AIの番号が設定されました")
        
        else:
            # 2人用の場合
            for i, player in enumerate([self.player1, self.player2], 1):
                print(f"\nプレイヤー{i}の番号設定（他のプレイヤーには見えません）")
                while True:
                    try:
                        player_input = input(f"プレイヤー{i}の番号（3桁の数字）: ").strip()
                        if len(player_input) != 3 or not player_input.isdigit():
                            print("3桁の数字を入力してください")
                            continue
                        
                        player_number = [int(d) for d in player_input]
                        if len(set(player_number)) != 3:
                            print("数字の重複は禁止です")
                            continue
                        
                        player.set_number(player_number)
                        break
                    except (ValueError, KeyboardInterrupt):
                        print("正しい形式で入力してください")
                        continue
                
                # 画面をクリア（番号を隠すため）
                os.system('clear' if os.name == 'posix' else 'cls')
    
    def calculate_eat_bite(self, answer: List[int], guess: List[int]) -> Tuple[int, int]:
        """EATとBITEを計算する"""
        eat = sum(a == g for a, g in zip(answer, guess))
        bite = sum(min(answer.count(d), guess.count(d)) for d in set(guess)) - eat
        return eat, bite
    
    def process_item_effect(self, player: Player, item: Item, opponent: Player) -> Dict[str, Any]:
        """アイテム効果を処理する"""
        result = {'effect': '', 'game_ended': False}
        
        if item.name == "DOUBLE":
            result['effect'] = "DOUBLEアイテムを使用しました。2回連続でコールできます。"
            player.double_call_count = 2
            # 1桁を開示
            reveal_pos = random.randint(0, 2)
            player.double_revealed_digit = reveal_pos
            result['effect'] += f"\n{player.name}の{reveal_pos + 1}桁目が開示されました: {player.number[reveal_pos]}"
        
        elif item.name == "HIGH&LOW":
            high_low_info = []
            for i, digit in enumerate(opponent.number):
                if digit >= 5:
                    high_low_info.append(f"{i+1}桁目: HIGH({digit})")
                else:
                    high_low_info.append(f"{i+1}桁目: LOW({digit})")
            result['effect'] = f"HIGH&LOWアイテムを使用しました。\n" + "\n".join(high_low_info)
        
        elif item.name == "TARGET":
            # ランダムな数字を選択
            target_digit = random.randint(0, 9)
            if target_digit in opponent.number:
                pos = opponent.number.index(target_digit)
                result['effect'] = f"TARGETアイテムを使用しました。\n数字{target_digit}は{pos+1}桁目にあります。"
            else:
                result['effect'] = f"TARGETアイテムを使用しました。\n数字{target_digit}は含まれていません。"
        
        elif item.name == "SLASH":
            max_digit = max(opponent.number)
            min_digit = min(opponent.number)
            slash_number = max_digit - min_digit
            result['effect'] = f"SLASHアイテムを使用しました。\nスラッシュナンバー: {slash_number}"
        
        elif item.name == "SHUFFLE":
            old_number = player.number.copy()
            random.shuffle(player.number)
            result['effect'] = f"SHUFFLEアイテムを使用しました。\n番号を並べ替えました: {old_number} → {player.number}"
        
        elif item.name == "CHANGE":
            # 簡単な実装: ランダムに1桁を変更
            pos = random.randint(0, 2)
            old_digit = player.number[pos]
            # 使用可能な数字から選択（重複を避ける）
            available_digits = [d for d in range(10) if d not in player.number]
            if available_digits:
                new_digit = random.choice(available_digits)
                # 一時的に数字を変更
                temp_number = player.number.copy()
                temp_number[pos] = new_digit
                # 重複チェック
                if len(set(temp_number)) == 3:
                    player.number[pos] = new_digit
                    result['effect'] = f"CHANGEアイテムを使用しました。\n{pos+1}桁目を{old_digit}から{new_digit}に変更しました。"
                else:
                    result['effect'] = "CHANGEアイテムを使用しましたが、変更により重複が発生するため変更できませんでした。"
            else:
                result['effect'] = "CHANGEアイテムを使用しましたが、変更可能な数字がありませんでした。"
        
        return result
    
    def display_game_state(self):
        """ゲーム状態を表示する"""
        print("\n" + "="*60)
        print(f"ターン {self.turn_count + 1} - {self.current_player.name}のターン")
        print("="*60)
        
        if self.mode == GameMode.SINGLE_PLAYER:
            print(f"プレイヤーの番号: {self.player1.number}")
            print("AIの番号: ???")
            # メモ用数字カードを表示
            self.display_memo_cards()
        else:
            print("プレイヤー1の番号: ???")
            print("プレイヤー2の番号: ???")
        
        # コール履歴を表示
        self.display_call_history()
        
        # アイテム状況を表示
        self.display_items_status()
    
    def display_call_history(self):
        """コール履歴を表示する"""
        print("\n--- コール履歴 ---")
        if not self.player1.call_history and not self.player2.call_history:
            print("まだコールがありません")
            return
        
        # 両プレイヤーの履歴を交互に表示
        max_history = max(len(self.player1.call_history), len(self.player2.call_history))
        for i in range(max_history):
            print(f"ターン {i+1}:")
            if i < len(self.player1.call_history):
                p1_call = self.player1.call_history[i]
                print(f"  {self.player1.name}: {p1_call['guess']} → {p1_call['eat']}EAT {p1_call['bite']}BITE")
            if i < len(self.player2.call_history):
                p2_call = self.player2.call_history[i]
                print(f"  {self.player2.name}: {p2_call['guess']} → {p2_call['eat']}EAT {p2_call['bite']}BITE")
    
    def display_memo_cards(self):
        """メモ用数字カードを表示する"""
        print("\n--- メモ用数字カード ---")
        print("使用済み/判明数字: ", end="")
        for i in range(10):
            if self.player1.memo_cards[i]:
                print(f"[{i}]", end=" ")
            else:
                print(f" {i} ", end=" ")
        print()
        
        # 判明した数字を表示
        if any(digit is not None for digit in self.player1.known_digits):
            print("判明した数字: ", end="")
            for i, digit in enumerate(self.player1.known_digits):
                if digit is not None:
                    print(f"{i+1}桁目: {digit}", end="  ")
            print()
    
    def display_items_status(self):
        """アイテム状況を表示する"""
        print("\n--- アイテム状況 ---")
        for player in [self.player1, self.player2]:
            print(f"{player.name}:")
            for item in player.items:
                print(f"  {item}")
    
    def play_turn(self):
        """1ターンを実行する"""
        self.display_game_state()
        
        # アイテム使用の確認
        item = self.current_player.choose_item(self.get_opponent())
        if item:
            item.use()
            self.current_player.used_items_this_turn = True
            result = self.process_item_effect(self.current_player, item, self.get_opponent())
            print(f"\n{item.name}アイテムの効果:")
            print(result['effect'])
            input("Enterキーを押して続行...")
        
        # コール処理
        if self.current_player.double_call_count > 0:
            # DOUBLEアイテム使用中
            self.current_player.double_call_count -= 1
            print(f"\n{self.current_player.name}のコール（DOUBLE残り{self.current_player.double_call_count}回）:")
        else:
            print(f"\n{self.current_player.name}のコール:")
        
        guess = self.current_player.make_guess(self.get_opponent())
        opponent = self.get_opponent()
        eat, bite = self.calculate_eat_bite(opponent.number, guess)
        
        # 履歴に追加
        item_used = item.name if item else None
        self.current_player.add_call_to_history(guess, eat, bite, item_used)
        self.current_player.update_memo_cards(guess)
        
        print(f"推測: {guess} → {eat}EAT {bite}BITE")
        
        # 勝利判定
        if eat == 3:
            self.game_ended = True
            self.winner = self.current_player
            print(f"\n🎉 {self.current_player.name}の勝利！")
            return
        
        # AIの場合は可能な番号を更新
        if isinstance(self.current_player, AIPlayer):
            self.current_player.update_possible_numbers(guess, eat, bite)
        
        # ターン終了処理
        self.current_player.reset_turn()
        self.current_player = self.get_opponent()
        self.turn_count += 1
        
        input("Enterキーを押して続行...")
    
    def get_opponent(self) -> Player:
        """対戦相手を取得する"""
        return self.player2 if self.current_player == self.player1 else self.player1
    
    def play_game(self):
        """ゲームを実行する"""
        print("🎮 数字当てゲーム（3桁戦）＋アイテム付き 🎮")
        print("="*60)
        
        self.initialize_players()
        self.setup_numbers()
        
        while not self.game_ended:
            self.play_turn()
        
        print(f"\n🏆 ゲーム終了！勝者: {self.winner.name}")
        print(f"総ターン数: {self.turn_count + 1}")


def main():
    """メイン関数"""
    print("数字当てゲーム（3桁戦）＋アイテム付き")
    print("="*50)
    print("1. 1人用（人間 vs AI）")
    print("2. 2人用（人間 vs 人間）")
    
    while True:
        try:
            choice = input("\nゲームモードを選択してください (1-2): ").strip()
            if choice == "1":
                game = NumeronGame(GameMode.SINGLE_PLAYER)
                break
            elif choice == "2":
                game = NumeronGame(GameMode.TWO_PLAYER)
                break
            else:
                print("1または2を入力してください")
        except KeyboardInterrupt:
            print("\nゲームを終了します")
            sys.exit(0)
    
    try:
        game.play_game()
    except KeyboardInterrupt:
        print("\n\nゲームを中断しました")
        sys.exit(0)


if __name__ == "__main__":
    main()
