#一个猜数字的游戏
'''游戏特点：
🎯 核心功能：
4种难度级别：从简单到地狱模式

智能提示系统：高低提示 + 距离提示 + 趋势提示

计分系统：基于剩余机会和难度计算得分

游戏统计：记录最佳成绩和总得分

🎮 游戏体验：
美观的界面：使用表情符号和格式化输出

错误处理：防止无效输入导致的崩溃

进度显示：实时显示剩余机会和猜测历史

暂停继续：游戏间有适当的暂停

📊 额外功能：
游戏统计：查看历史成绩

详细说明：完整的游戏规则说明

最佳记录：追踪最佳表现'''
import random
import time
import os

class NumberGuessingGame:
    def __init__(self):
        self.score = 0
        self.total_games = 0
        self.best_score = float('inf')
        
    def clear_screen(self):
        """清空屏幕"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_welcome(self):
        """显示欢迎信息"""
        print("🎯 欢迎来到猜数字游戏！")
        print("=" * 40)
        print("游戏规则：")
        print("1. 我会随机生成一个数字")
        print("2. 你需要猜出这个数字是多少")
        print("3. 每次猜测后我会给你提示")
        print("4. 猜的次数越少，得分越高！")
        print("=" * 40)
    
    def choose_difficulty(self):
        """选择难度级别"""
        print("\n请选择难度级别：")
        print("1. 简单模式 (1-50，10次机会)")
        print("2. 普通模式 (1-100，7次机会)")
        print("3. 困难模式 (1-200，5次机会)")
        print("4. 地狱模式 (1-500，3次机会)")
        
        while True:
            try:
                choice = int(input("请输入选择 (1-4): "))
                if 1 <= choice <= 4:
                    return choice
                else:
                    print("请输入 1-4 之间的数字！")
            except ValueError:
                print("请输入有效的数字！")
    
    def get_game_settings(self, difficulty):
        """根据难度返回游戏设置"""
        settings = {
            1: {"range": (1, 50), "chances": 10, "name": "简单模式"},
            2: {"range": (1, 100), "chances": 7, "name": "普通模式"},
            3: {"range": (1, 200), "chances": 5, "name": "困难模式"},
            4: {"range": (1, 500), "chances": 3, "name": "地狱模式"}
        }
        return settings[difficulty]
    
    def get_hint(self, guess, target, previous_guess=None):
        """提供猜测提示"""
        if guess == target:
            return "🎉 恭喜！猜对了！"
        
        # 距离提示
        difference = abs(guess - target)
        if difference <= 5:
            distance_hint = "非常接近！"
        elif difference <= 15:
            distance_hint = "比较接近"
        elif difference <= 30:
            distance_hint = "有点远"
        else:
            distance_hint = "很远"
        
        # 高低提示
        if guess < target:
            direction_hint = "低了 📉"
        else:
            direction_hint = "高了 📈"
        
        # 趋势提示（如果有上一次猜测）
        trend_hint = ""
        if previous_guess:
            prev_diff = abs(previous_guess - target)
            current_diff = abs(guess - target)
            if current_diff < prev_diff:
                trend_hint = "更接近了！ 👍"
            else:
                trend_hint = "更远了 👎"
        
        return f"{direction_hint} | {distance_hint} {trend_hint}"
    
    def calculate_score(self, chances_used, total_chances, difficulty):
        """计算得分"""
        base_score = 1000
        chance_bonus = (total_chances - chances_used) * 100
        difficulty_multiplier = difficulty * 0.5
        
        score = (base_score + chance_bonus) * difficulty_multiplier
        return int(score)
    
    def play_round(self):
        """进行一轮游戏"""
        self.clear_screen()
        self.display_welcome()
        
        # 选择难度
        difficulty = self.choose_difficulty()
        settings = self.get_game_settings(difficulty)
        
        # 生成目标数字
        target_number = random.randint(settings["range"][0], settings["range"][1])
        chances = settings["chances"]
        previous_guess = None
        
        print(f"\n🎮 开始 {settings['name']}！")
        print(f"📊 数字范围: {settings['range'][0]} - {settings['range'][1]}")
        print(f"💡 你有 {chances} 次机会")
        print("─" * 30)
        
        for attempt in range(1, chances + 1):
            print(f"\n第 {attempt}/{chances} 次尝试")
            
            while True:
                try:
                    guess = int(input("请输入你猜的数字: "))
                    if settings["range"][0] <= guess <= settings["range"][1]:
                        break
                    else:
                        print(f"数字必须在 {settings['range'][0]} 到 {settings['range'][1]} 之间！")
                except ValueError:
                    print("请输入有效的数字！")
            
            # 检查猜测结果
            hint = self.get_hint(guess, target_number, previous_guess)
            print(f"💡 提示: {hint}")
            
            if guess == target_number:
                # 猜对了
                score = self.calculate_score(attempt, chances, difficulty)
                self.score += score
                self.total_games += 1
                
                if attempt < self.best_score:
                    self.best_score = attempt
                
                print(f"\n🎊 太棒了！你在第 {attempt} 次猜对了！")
                print(f"💰 本轮得分: {score}")
                print(f"🏆 总得分: {self.score}")
                print(f"📈 最佳记录: {self.best_score} 次猜中")
                break
            
            previous_guess = guess
            
            # 显示剩余机会
            remaining = chances - attempt
            if remaining > 0:
                print(f"📋 还剩 {remaining} 次机会")
            else:
                print(f"\n💀 游戏结束！正确的数字是: {target_number}")
                self.total_games += 1
                break
            
            print("─" * 30)
    
    def show_statistics(self):
        """显示游戏统计"""
        if self.total_games > 0:
            avg_attempts = self.best_score if self.best_score != float('inf') else 0
            print("\n📊 游戏统计:")
            print(f"  总游戏轮数: {self.total_games}")
            print(f"  累计得分: {self.score}")
            print(f"  最佳记录: {avg_attempts} 次猜中")
        else:
            print("\n还没有游戏记录，快来玩一局吧！")
    
    def main_menu(self):
        """主菜单"""
        while True:
            self.clear_screen()
            print("🎯 猜数字游戏")
            print("=" * 30)
            print("1. 开始游戏")
            print("2. 查看统计")
            print("3. 游戏说明")
            print("4. 退出游戏")
            print("=" * 30)
            
            choice = input("请选择 (1-4): ").strip()
            
            if choice == "1":
                self.play_round()
                input("\n按回车键继续...")
            elif choice == "2":
                self.clear_screen()
                self.show_statistics()
                input("\n按回车键返回主菜单...")
            elif choice == "3":
                self.clear_screen()
                self.display_instructions()
                input("\n按回车键返回主菜单...")
            elif choice == "4":
                print("\n谢谢游玩！再见！👋")
                break
            else:
                print("无效选择，请重新输入！")
                time.sleep(1)
    
    def display_instructions(self):
        """显示游戏说明"""
        print("📖 游戏说明")
        print("=" * 40)
        print("游戏目标：在有限的次数内猜出随机数字")
        print("\n难度级别：")
        print("  🟢 简单: 1-50，10次机会")
        print("  🟡 普通: 1-100，7次机会")
        print("  🟠 困难: 1-200，5次机会")
        print("  🔴 地狱: 1-500，3次机会")
        print("\n得分规则：")
        print("  • 剩余机会越多，得分越高")
        print("  • 难度越高，得分倍数越高")
        print("  • 猜中次数越少，记录越好")
        print("\n提示系统：")
        print("  • 高低提示（高了/低了）")
        print("  • 距离提示（非常接近/比较接近等）")
        print("  • 趋势提示（更接近/更远了）")

def main():
    """主函数"""
    game = NumberGuessingGame()
    game.main_menu()

if __name__ == "__main__":
    main()