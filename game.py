import tkinter as tk
import random
import os

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
HIGHSCORE_FILE = "highscore.txt"

class CatchCoinGame:
    def __init__(self, root):
        self.root = root
        self.root.title("歡樂接金幣 - 紀錄挑戰極限版")
        
        # 建立畫布
        self.canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg="#87CEEB")
        self.canvas.pack()
        
        # 玩家基本設定
        self.player_width = 100
        self.player_height = 20
        self.player_y = SCREEN_HEIGHT - 40
        self.player_speed = 35  
        self.item_radius = 15
        
        # 綁定鍵盤
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<r>", self.restart_game)
        self.root.bind("<R>", self.restart_game)
        
        # UI 文字 (調整了間距，並加入 High Score 顯示欄位)
        self.score_text = self.canvas.create_text(20, 20, text="", anchor="nw", font=("Arial", 16, "bold"), fill="black")
        self.highscore_text = self.canvas.create_text(20, 45, text="", anchor="nw", font=("Arial", 16, "bold"), fill="#D2691E")
        self.lives_text = self.canvas.create_text(20, 70, text="", anchor="nw", font=("Arial", 16, "bold"), fill="red")
        self.level_text = self.canvas.create_text(20, 95, text="", anchor="nw", font=("Arial", 16, "bold"), fill="#00008B")
        self.next_level_text = self.canvas.create_text(20, 120, text="", anchor="nw", font=("Arial", 12, "italic"), fill="#444444")
        
        self.time_text = self.canvas.create_text(SCREEN_WIDTH - 20, 20, text="", anchor="ne", font=("Arial", 18, "bold"), fill="black")
        self.item_hint_text = self.canvas.create_text(SCREEN_WIDTH // 2, 20, text="", anchor="n", font=("Arial", 16, "bold"), fill="blue")
        
        # 玩家板子
        self.player = self.canvas.create_rectangle(0, 0, 0, 0, fill="#2E8B57", outline="")
        
        # 多道具追蹤清單
        self.active_items = []
        
        self.game_over = False
        self.time_counter = 0  
        self.spawn_counter = 0  
        
        # 載入歷史最高分
        self.high_score = self.load_highscore()
        
        self.setup_game()

    def load_highscore(self):
        """從檔案讀取最高分，如果檔案不存在就從 0 開始"""
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, "r") as f:
                    return int(f.read().strip())
            except:
                return 0
        return 0

    def save_highscore(self):
        """將新的最高分寫入檔案存檔"""
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(self.high_score))
        except Exception as e:
            print(f"無法儲存最高分: {e}")

    def setup_game(self):
        self.canvas.delete("gameover_msg")
        
        # 清除上一局殘留的道具
        for item in self.active_items:
            self.canvas.delete(item["obj_id"])
        self.active_items.clear()
        
        # 初始化數據
        self.game_over = False
        self.score = 0
        self.lives = 3
        self.level = 1          
        self.time_left = 60
        self.time_counter = 0
        self.spawn_counter = 0
        
        # 門檻遞增核心機制
        self.score_target_for_next_level = 10  
        
        # 難度核心參數
        self.base_speed_min = 3.5  
        self.base_speed_max = 5.5  
        self.spawn_interval = 40   
        
        # 重置玩家位置
        self.player_x = (SCREEN_WIDTH - self.player_width) // 2
        self.canvas.coords(self.player, self.player_x, self.player_y, self.player_x + self.player_width, self.player_y + self.player_height)
        
        # 刷新 UI 文字
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
        self.canvas.itemconfig(self.highscore_text, text=f"High Score: {self.high_score}")
        self.canvas.itemconfig(self.lives_text, text=f"Lives: {'❤️' * self.lives}")
        self.canvas.itemconfig(self.level_text, text=f"Level: {self.level}")
        self.canvas.itemconfig(self.time_text, text=f"Time: {self.time_left}s")
        self.canvas.itemconfig(self.item_hint_text, text="")
        self.update_next_level_ui()
        
        # 初始生成
        self.spawn_new_item()
        self.main_tick()

    def spawn_new_item(self):
        max_allowed = min(5 + self.level, 8)
        if len(self.active_items) >= max_allowed:
            return
            
        item_x = random.randint(self.item_radius, SCREEN_WIDTH - self.item_radius)
        item_y = -20  
        
        rand_num = random.random()
        speed_bonus = (self.level - 1) * 1.3
        
        if rand_num < 0.55:
            item_type = "coin"
            color = "#FFD700"  
            speed = random.uniform(self.base_speed_min, self.base_speed_max) + speed_bonus
        elif rand_num < 0.70:
            item_type = "star"
            color = "#9400D3"  
            speed = random.uniform(self.base_speed_min + 1.5, self.base_speed_max + 1.5) + speed_bonus
        else:
            item_type = "bomb"
            color = "#FF4500"  
            speed = random.uniform(self.base_speed_min + 0.5, self.base_speed_max + 1.0) + speed_bonus
            
        obj_id = self.canvas.create_oval(
            item_x - self.item_radius, item_y - self.item_radius,
            item_x + self.item_radius, item_y + self.item_radius,
            fill=color, outline=""
        )
        
        self.active_items.append({
            "obj_id": obj_id,
            "type": item_type,
            "speed": speed
        })

    def check_level_up(self):
        while self.score >= self.score_target_for_next_level:
            self.level += 1
            next_requirement = self.level * 10
            self.score_target_for_next_level += next_requirement
            
            self.canvas.itemconfig(self.level_text, text=f"Level: {self.level}")
            self.canvas.itemconfig(self.item_hint_text, text=f"🎉 LEVEL UP! Level {self.level} 🎉", fill="#FF4500")
            self.spawn_interval = max(16, 40 - (self.level - 1) * 6)
            
        self.update_next_level_ui()

    def update_next_level_ui(self):
        points_needed = self.score_target_for_next_level - self.score
        self.canvas.itemconfig(self.next_level_text, text=f"Next Level: {points_needed} pts needed")

    def move_left(self, event):
        if self.game_over: return
        coords = self.canvas.coords(self.player)
        if coords[0] > 0: self.canvas.move(self.player, -self.player_speed, 0)

    def move_right(self, event):
        if self.game_over: return
        coords = self.canvas.coords(self.player)
        if coords[2] < SCREEN_WIDTH: self.canvas.move(self.player, self.player_speed, 0)

    def main_tick(self):
        if self.game_over: return
        
        self.time_counter += 16
        if self.time_counter >= 1000:
            self.time_counter = 0
            self.time_left -= 1
            self.canvas.itemconfig(self.time_text, text=f"Time: {self.time_left}s")
            if self.time_left <= 0:
                self.end_game("TIME UP!\nYou Survived!")
                return
                
        self.spawn_counter += 1
        if self.spawn_counter >= self.spawn_interval:
            self.spawn_counter = 0
            self.spawn_new_item()
            
        player_coords = self.canvas.coords(self.player)
        
        for i in range(len(self.active_items) - 1, -1, -1):
            item = self.active_items[i]
            obj_id = item["obj_id"]
            
            self.canvas.move(obj_id, 0, item["speed"])
            item_coords = self.canvas.coords(obj_id)
            
            if item_coords[3] > SCREEN_HEIGHT:
                self.canvas.delete(obj_id)
                self.active_items.pop(i)
                continue
                
            elif (item_coords[3] >= player_coords[1] and item_coords[1] <= player_coords[3] and
                  item_coords[2] >= player_coords[0] and item_coords[0] <= player_coords[2]):
                
                if item["type"] == "coin":
                    self.score += 1
                    self.canvas.itemconfig(self.item_hint_text, text="+1 Coin", fill="blue")
                elif item["type"] == "star":
                    self.score += 3
                    self.canvas.itemconfig(self.item_hint_text, text="⭐ LUCKY! +3 Points ⭐", fill="#9400D3")
                elif item["type"] == "bomb":
                    self.lives -= 1
                    self.canvas.itemconfig(self.item_hint_text, text="💥 BOMB! Lives -1 💥", fill="black")
                    self.canvas.itemconfig(self.lives_text, text=f"Lives: {'❤️' * self.lives}")
                    if self.lives <= 0:
                        self.canvas.itemconfig(self.lives_text, text="Lives: ☠️")
                        self.end_game("GAME OVER\nBlasted by Bomb!")
                        return
                
                self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
                
                # 即時檢查即時更新最高分 UI
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.canvas.itemconfig(self.highscore_text, text=f"High Score: {self.high_score}", fill="#FF4500")
                
                self.check_level_up()
                self.canvas.delete(obj_id)
                self.active_items.pop(i)
                continue
                
        self.root.after(16, self.main_tick)

    def end_game(self, message):
        self.game_over = True
        self.canvas.itemconfig(self.item_hint_text, text="")
        
        # 遊戲結束時將最終最高分寫入外部檔案儲存
        self.save_highscore()
        
        self.canvas.create_text(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, 
            text=f"{message}\nFinal Score: {self.score}\nBest Score: {self.high_score}", 
            font=("Arial", 26, "bold"), fill="black", justify="center", tags="gameover_msg"
        )
        self.canvas.create_text(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70, 
            text="Press [R] to Restart", 
            font=("Arial", 20, "italic"), fill="#444444", tags="gameover_msg"
        )

    def restart_game(self, event):
        if self.game_over:
            self.setup_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = CatchCoinGame(root)
    root.mainloop()