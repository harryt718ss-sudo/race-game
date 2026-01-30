

# 簡單賽車遊戲
import tkinter as tk
import random

class RacingGame:
    def __init__(self, master):
        self.master = master
        self.master.title('賽車遊戲')
        self.width = 400
        self.height = 600 * 20  # 畫布高度放大 20 倍
        self.road_w = 300  # 拓寬賽道
        self.road_x = (self.width - self.road_w) // 2
        self.finish_line = 80 * 20  # 終點線 y 座標（放遠 20 倍）
        self.canvas = tk.Canvas(master, width=self.width, height=self.height, bg='darkgreen')
        self.canvas.pack()
        self.score = 0
        self.score_label = tk.Label(master, text=f'分數: {self.score}', font=('Arial', 14))
        self.score_label.pack()

        # 車子模型
        self.car_w = 40
        self.car_h = 70
        self.car_x = self.width // 2
        self.car_y = self.height - 100

        # 對手車
        self.rival_w = 40
        self.rival_h = 70
        self.rival_x = self.width // 2
        self.rival_y = 200
        self.rival_dir_x = 1  # 1: 右, -1: 左
        self.rival_dir_y = 0  # 1: 下, -1: 上, 0: 不動
        self.rival_speed_x = 8
        self.rival_speed_y = 8

        self.obstacles = []  # [(x, y)]
        self.obstacle_w = 40
        self.obstacle_h = 70
        self.obstacle_speed = 7
        self.running = True

        self.master.bind('<Left>', self.move_left)
        self.master.bind('<Right>', self.move_right)
        self.master.bind('<Up>', self.move_up)
        self.master.bind('<Down>', self.move_down)
        self.master.bind('<KeyPress-Shift_L>', self.shift_down)
        self.master.bind('<KeyRelease-Shift_L>', self.shift_up)
        self.master.bind('<KeyPress-Shift_R>', self.shift_down)
        self.master.bind('<KeyRelease-Shift_R>', self.shift_up)
        self.master.bind('<Return>', self.restart_game)
        self.speed = 30
        self.fast_speed = 60
        self.vertical_speed = 20
        self.is_fast = False
        self.rival_move_counter = 0
        self.player_slow_timer = 0
        self.rival_slow_timer = 0
        self.slow_duration = 30  # 幀數
        self.slow_factor = 0.4  # 減速比例
        self.game_winner = None
        self.update()
    def move_up(self, event):
        speed = self.vertical_speed
        if self.player_slow_timer > 0:
            speed = int(self.vertical_speed * self.slow_factor)
        if self.car_y - self.car_h//2 > 0:
            self.car_y -= speed

    def move_down(self, event):
        speed = self.vertical_speed
        if self.player_slow_timer > 0:
            speed = int(self.vertical_speed * self.slow_factor)
        if self.car_y + self.car_h//2 < self.height:
            self.car_y += speed

    def move_left(self, event):
        move = self.fast_speed if self.is_fast else self.speed
        if self.player_slow_timer > 0:
            move = int(move * self.slow_factor)
        if self.car_x - self.car_w//2 > self.road_x:
            self.car_x -= move

    def move_right(self, event):
        move = self.fast_speed if self.is_fast else self.speed
        if self.player_slow_timer > 0:
            move = int(move * self.slow_factor)
        if self.car_x + self.car_w//2 < self.road_x + self.road_w:
            self.car_x += move

    def shift_down(self, event):
        self.is_fast = True

    def shift_up(self, event):
        self.is_fast = False

    def restart_game(self, event):
        if not self.running:
            self.score = 0
            self.car_x = self.width // 2
            self.car_y = self.height - 100
            self.obstacles = []
            # 重設對手車
            self.rival_x = self.width // 2
            self.rival_y = 200
            self.rival_dir_x = 1
            self.rival_dir_y = 0
            self.rival_move_counter = 0
            self.running = True
            self.update()

    def spawn_obstacle(self):
        x = random.randint(self.road_x + self.obstacle_w//2, self.road_x + self.road_w - self.obstacle_w//2)
        self.obstacles.append([x, -self.obstacle_h])

    def update(self):
        if not self.running:
            self.canvas.create_text(self.width//2, self.height//2, text='遊戲結束', fill='white', font=('Arial', 32))
            self.canvas.create_text(self.width//2, self.height//2+40, text='按 Enter 重新開始', fill='yellow', font=('Arial', 18))
            return
        # 移動障礙物
        for obs in self.obstacles:
            obs[1] += self.obstacle_speed
        # 移除超出畫面的障礙物並加分
        self.obstacles = [obs for obs in self.obstacles if obs[1] < self.height]
        # 檢查玩家車碰撞障礙物
        for obs in self.obstacles:
            if (abs(obs[0] - self.car_x) < (self.obstacle_w + self.car_w)//2) and (abs(obs[1] - self.car_y) < (self.obstacle_h + self.car_h)//2):
                # 玩家車撞到障礙物，彈開
                if self.car_y > obs[1]:
                    self.car_y = min(self.height - self.car_h//2, self.car_y + 40)
                else:
                    self.car_y = max(self.car_h//2, self.car_y - 40)

        # 檢查對手車碰撞障礙物
        for obs in self.obstacles:
            if (abs(obs[0] - self.rival_x) < (self.obstacle_w + self.rival_w)//2) and (abs(obs[1] - self.rival_y) < (self.obstacle_h + self.rival_h)//2):
                # 對手車撞到障礙物，彈開
                if self.rival_y > obs[1]:
                    self.rival_y = min(self.height - self.rival_h//2, self.rival_y + 40)
                else:
                    self.rival_y = max(self.rival_h//2, self.rival_y - 40)

        # 對手車隨機左右與前後移動
        self.rival_move_counter += 1
        if self.rival_move_counter % 15 == 0:
            # 每15幀隨機改變方向
            self.rival_dir_x = random.choice([-1, 0, 1])
            self.rival_dir_y = random.choice([-1, 0, 1])
        rival_speed_x = self.rival_speed_x
        rival_speed_y = self.rival_speed_y
        if self.rival_slow_timer > 0:
            rival_speed_x = int(self.rival_speed_x * self.slow_factor)
            rival_speed_y = int(self.rival_speed_y * self.slow_factor)
        self.rival_x += self.rival_dir_x * rival_speed_x
        self.rival_y += self.rival_dir_y * rival_speed_y
        # 限制對手車在賽道範圍內
        if self.rival_x - self.rival_w//2 < self.road_x:
            self.rival_x = self.road_x + self.rival_w//2
            self.rival_dir_x *= -1
        elif self.rival_x + self.rival_w//2 > self.road_x + self.road_w:
            self.rival_x = self.road_x + self.road_w - self.rival_w//2
            self.rival_dir_x *= -1
        if self.rival_y - self.rival_h//2 < 0:
            self.rival_y = self.rival_h//2
            self.rival_dir_y *= -1
        elif self.rival_y + self.rival_h//2 > self.height:
            self.rival_y = self.height - self.rival_h//2
            self.rival_dir_y *= -1

        # 玩家車與對手車碰撞，雙方彈開並減速
        if (abs(self.car_x - self.rival_x) < (self.car_w + self.rival_w)//2) and (abs(self.car_y - self.rival_y) < (self.car_h + self.rival_h)//2):
            # 垂直方向彈開
            if self.car_y < self.rival_y:
                self.car_y = max(self.car_h//2, self.car_y - 40)
                self.rival_y = min(self.height - self.rival_h//2, self.rival_y + 40)
            else:
                self.car_y = min(self.height - self.car_h//2, self.car_y + 40)
                self.rival_y = max(self.rival_h//2, self.rival_y - 40)
            # 水平方向彈開
            if self.car_x < self.rival_x:
                self.car_x = max(self.road_x + self.car_w//2, self.car_x - 40)
                self.rival_x = min(self.road_x + self.road_w - self.rival_w//2, self.rival_x + 40)
            else:
                self.car_x = min(self.road_x + self.road_w - self.car_w//2, self.car_x + 40)
                self.rival_x = max(self.road_x + self.rival_w//2, self.rival_x - 40)
            # 雙方減速
            self.player_slow_timer = self.slow_duration
            self.rival_slow_timer = self.slow_duration

        # 產生新障礙物
        if random.random() < 0.03:
            self.spawn_obstacle()
        # 計分
        self.score += 1
        self.score_label.config(text=f'分數: {self.score // 10}')

        # 減速計時器遞減
        if self.player_slow_timer > 0:
            self.player_slow_timer -= 1
        if self.rival_slow_timer > 0:
            self.rival_slow_timer -= 1

        # 終點判斷
        if self.car_y - self.car_h//2 <= self.finish_line:
            self.running = False
            self.game_winner = '玩家'
        elif self.rival_y - self.rival_h//2 <= self.finish_line:
            self.running = False
            self.game_winner = '對手'

        self.draw()
        self.master.after(30, self.update)

    def draw(self):
        self.canvas.delete('all')
        # 畫賽道
        self.canvas.create_rectangle(self.road_x, 0, self.road_x + self.road_w, self.height, fill='gray')
        # 畫終點線
        self.canvas.create_rectangle(self.road_x, self.finish_line, self.road_x + self.road_w, self.finish_line+6, fill='yellow')
        self.canvas.create_text(self.road_x + 30, self.finish_line+18, text='終點', fill='yellow', font=('Arial', 14))
        # 畫賽道中線
        for y in range(0, self.height, 40):
            self.canvas.create_rectangle(self.width//2 - 5, y, self.width//2 + 5, y+20, fill='white', width=0)
        # 畫玩家車子（藍色）
        x, y = self.car_x, self.car_y
        self.canvas.create_rectangle(x - self.car_w//2, y - self.car_h//2, x + self.car_w//2, y + self.car_h//2, fill='blue', outline='black', width=2)
        self.canvas.create_rectangle(x - 12, y - 25, x + 12, y - 5, fill='skyblue', outline='black')  # 車窗
        self.canvas.create_oval(x - self.car_w//2 - 6, y - 20, x - self.car_w//2 + 6, y - 8, fill='black')  # 左輪
        self.canvas.create_oval(x + self.car_w//2 - 6, y - 20, x + self.car_w//2 + 6, y - 8, fill='black')  # 右輪
        self.canvas.create_oval(x - self.car_w//2 - 6, y + 20, x - self.car_w//2 + 6, y + 32, fill='black')  # 左輪
        self.canvas.create_oval(x + self.car_w//2 - 6, y + 20, x + self.car_w//2 + 6, y + 32, fill='black')  # 右輪
        # 畫對手車（綠色）
        rx, ry = self.rival_x, self.rival_y
        self.canvas.create_rectangle(rx - self.rival_w//2, ry - self.rival_h//2, rx + self.rival_w//2, ry + self.rival_h//2, fill='green', outline='black', width=2)
        self.canvas.create_rectangle(rx - 12, ry - 25, rx + 12, ry - 5, fill='lightgreen', outline='black')
        self.canvas.create_oval(rx - self.rival_w//2 - 6, ry - 20, rx - self.rival_w//2 + 6, ry - 8, fill='black')
        self.canvas.create_oval(rx + self.rival_w//2 - 6, ry - 20, rx + self.rival_w//2 + 6, ry - 8, fill='black')
        self.canvas.create_oval(rx - self.rival_w//2 - 6, ry + 20, rx - self.rival_w//2 + 6, ry + 32, fill='black')
        self.canvas.create_oval(rx + self.rival_w//2 - 6, ry + 20, rx + self.rival_w//2 + 6, ry + 32, fill='black')
        # 畫障礙物（紅色車型）
        for ox, oy in self.obstacles:
            self.canvas.create_rectangle(ox - self.obstacle_w//2, oy - self.obstacle_h//2, ox + self.obstacle_w//2, oy + self.obstacle_h//2, fill='red', outline='black', width=2)
            self.canvas.create_rectangle(ox - 12, oy - 25, ox + 12, oy - 5, fill='pink', outline='black')
            self.canvas.create_oval(ox - self.obstacle_w//2 - 6, oy - 20, ox - self.obstacle_w//2 + 6, oy - 8, fill='black')
            self.canvas.create_oval(ox + self.obstacle_w//2 - 6, oy - 20, ox + self.obstacle_w//2 + 6, oy - 8, fill='black')
            self.canvas.create_oval(ox - self.obstacle_w//2 - 6, oy + 20, ox - self.obstacle_w//2 + 6, oy + 32, fill='black')
            self.canvas.create_oval(ox + self.obstacle_w//2 - 6, oy + 20, ox + self.obstacle_w//2 + 6, oy + 32, fill='black')

        # 顯示勝利者
        if not self.running and self.game_winner:
            self.canvas.create_text(self.width//2, self.height//2, text=f'{self.game_winner}獲勝！', fill='gold', font=('Arial', 32))
            self.canvas.create_text(self.width//2, self.height//2+40, text='按 Enter 重新開始', fill='yellow', font=('Arial', 18))

if __name__ == '__main__':
    root = tk.Tk()
    game = RacingGame(root)
    root.mainloop()
