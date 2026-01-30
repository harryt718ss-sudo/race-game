import tkinter as tk
import random
import math

class RacingGame:
    def __init__(self, master):
        self.master = master
        self.master.title('彎道賽車遊戲')
        self.width = 400
        self.height = 600
        self.road_w = 300
        self.road_x_base = (self.width - self.road_w) // 2
        self.finish_line = 80 * 40
        self.world_height = 600 * 40
        self.canvas = tk.Canvas(master, width=self.width, height=self.height, bg='darkgreen')
        self.canvas.pack()
        self.info_label = tk.Label(master, text='', font=('Arial', 14))
        self.info_label.pack()

        # 玩家車
        self.car_w = 40
        self.car_h = 70
        self.car_x = self.width // 2
        self.car_y = self.world_height - 100

        # 對手車
        self.rival_w = 40
        self.rival_h = 70
        self.rival_x = self.width // 2 + 60
        self.rival_y = self.world_height - 100
        self.rival_dir_x = 0
        self.rival_dir_y = 0

        # 速度設定
        self.base_speed = 30
        self.fast_speed = 40
        self.is_fast = False
        self.fast_timer = 0  # 加速剩餘幀數
        self.fast_timer_max = 30  # 1秒(30fps)
        self.fast_cooldown = False
        self.fast_used = False  # 玩家加速僅限一次

        # 障礙車
        self.obstacle_w = 40
        self.obstacle_h = 70
        self.obstacles = []  # [(x, y, color)]
        self.max_obstacles = 60  # 增加障礙車數（3倍）

        self.running = True
        self.game_winner = None
        self.camera_offset = 0
        self.pressed_keys = set()

        self.master.bind('<KeyPress>', self.on_key_press)
        self.master.bind('<KeyRelease>', self.on_key_release)
        self.master.bind('<Return>', self.restart_game)
        self.update()

    def get_road_x(self, y):
        # 彎道設計：正弦波型彎道，幅度加大
        return self.road_x_base + int(140 * math.sin(y / 800))

    def spawn_obstacle(self):
        y = random.randint(0, self.world_height - 200)
        road_x = self.get_road_x(y)
        x = random.randint(road_x + self.obstacle_w//2, road_x + self.road_w - self.obstacle_w//2)
        color = random.choice(['red', 'orange', 'purple', 'brown', 'gray'])
        self.obstacles.append([x, y, color])

    def on_key_press(self, event):
        self.pressed_keys.add(event.keysym)
        # 按空白鍵啟動加速（僅限一次）
        if event.keysym == 'space' and not self.fast_cooldown and self.fast_timer == 0 and not self.fast_used:
            self.is_fast = True
            self.fast_timer = self.fast_timer_max
            self.fast_cooldown = True
            self.fast_used = True

    def on_key_release(self, event):
        if event.keysym in self.pressed_keys:
            self.pressed_keys.remove(event.keysym)

    def restart_game(self, event):
        if not self.running:
            self.car_x = self.width // 2
            self.car_y = self.world_height - 100
            self.rival_x = self.width // 2 + 60
            self.rival_y = self.world_height - 100
            self.obstacles = []
            self.running = True
            self.game_winner = None
            self.fast_timer = 0
            self.fast_cooldown = False
            self.is_fast = False
            self.fast_used = False
            self.update()

    def move_player(self):
        # 判斷是否在賽道範圍
        road_x = self.get_road_x(self.car_y)
        on_road = (road_x + self.car_w//2 <= self.car_x <= road_x + self.road_w - self.car_w//2)
        move = self.fast_speed if self.is_fast else self.base_speed
        if not on_road:
            move = 10
        dx = dy = 0
        if 'Left' in self.pressed_keys and self.car_x - self.car_w//2 > 0:
            dx -= move
        if 'Right' in self.pressed_keys and self.car_x + self.car_w//2 < self.width:
            dx += move
        if 'Up' in self.pressed_keys and self.car_y - self.car_h//2 > 0:
            dy -= move
        if 'Down' in self.pressed_keys and self.car_y + self.car_h//2 < self.world_height:
            dy += move
        self.car_x += dx
        self.car_y += dy
        # 限制車子不出畫面
        self.car_x = max(self.car_w//2, min(self.width - self.car_w//2, self.car_x))

    def update(self):
        # 加速計時
        if self.fast_timer > 0:
            self.fast_timer -= 1
            if self.fast_timer == 0:
                self.is_fast = False
                self.fast_cooldown = True
        elif self.fast_cooldown and 'space' not in self.pressed_keys:
            self.fast_cooldown = False

        if not self.running:
            self.draw()
            return
        # 障礙車數量維持
        while len(self.obstacles) < self.max_obstacles:
            self.spawn_obstacle()

        # 玩家移動
        self.move_player()

        # 玩家與障礙車碰撞
        for obs in self.obstacles:
            if (abs(obs[0] - self.car_x) < (self.obstacle_w + self.car_w)//2) and (abs(obs[1] - self.car_y) < (self.obstacle_h + self.car_h)//2):
                if self.car_y > obs[1]:
                    self.car_y = min(self.world_height - self.car_h//2, self.car_y + 40)
                else:
                    self.car_y = max(self.car_h//2, self.car_y - 40)
        # 對手與障礙車碰撞
        for obs in self.obstacles:
            if (abs(obs[0] - self.rival_x) < (self.obstacle_w + self.rival_w)//2) and (abs(obs[1] - self.rival_y) < (self.obstacle_h + self.rival_h)//2):
                if self.rival_y > obs[1]:
                    self.rival_y = min(self.world_height - self.rival_h//2, self.rival_y + 40)
                else:
                    self.rival_y = max(self.rival_h//2, self.rival_y - 40)
        # 玩家與對手車碰撞
        if (abs(self.car_x - self.rival_x) < (self.car_w + self.rival_w)//2) and (abs(self.car_y - self.rival_y) < (self.car_h + self.rival_h)//2):
            if self.car_y < self.rival_y:
                self.car_y = max(self.car_h//2, self.car_y - 40)
                self.rival_y = min(self.world_height - self.rival_h//2, self.rival_y + 40)
            else:
                self.car_y = min(self.world_height - self.car_h//2, self.car_y + 40)
                self.rival_y = max(self.rival_h//2, self.rival_y - 40)
            if self.car_x < self.rival_x:
                self.car_x = max(self.get_road_x(self.car_y) + self.car_w//2, self.car_x - 40)
                self.rival_x = min(self.get_road_x(self.rival_y) + self.road_w - self.rival_w//2, self.rival_x + 40)
            else:
                self.car_x = min(self.get_road_x(self.car_y) + self.road_w - self.car_w//2, self.car_x + 40)
                self.rival_x = max(self.get_road_x(self.rival_y) + self.rival_w//2, self.rival_x - 40)

        # 對手 AI 控制（自動往終點，偶爾閃避障礙）
        self.rival_dir_x = 0
        self.rival_dir_y = -1
        road_x_rival = self.get_road_x(self.rival_y)
        for obs in self.obstacles:
            if abs(obs[1] - (self.rival_y - self.rival_h//2)) < 60 and abs(obs[0] - self.rival_x) < self.rival_w:
                self.rival_dir_x = random.choice([-1, 1])
                break
        rival_move = self.fast_speed if self.rival_y < self.car_y else self.base_speed
        if self.rival_x - self.rival_w//2 > road_x_rival and self.rival_dir_x == -1:
            self.rival_x -= rival_move
        if self.rival_x + self.rival_w//2 < road_x_rival + self.road_w and self.rival_dir_x == 1:
            self.rival_x += rival_move
        if self.rival_y - self.rival_h//2 > 0 and self.rival_dir_y == -1:
            self.rival_y -= rival_move
        if self.rival_y + self.rival_h//2 < self.world_height and self.rival_dir_y == 1:
            self.rival_y += rival_move
        self.rival_x = max(road_x_rival + self.rival_w//2, min(road_x_rival + self.road_w - self.rival_w//2, self.rival_x))

        # 終點判斷
        if self.car_y - self.car_h//2 <= self.finish_line:
            self.running = False
            self.game_winner = '玩家'
        elif self.rival_y - self.rival_h//2 <= self.finish_line:
            self.running = False
            self.game_winner = '對手'

        # 畫面跟隨玩家
        self.camera_offset = self.car_y - self.height // 2
        self.camera_offset = max(0, min(self.camera_offset, self.world_height - self.height))

        # 顯示加速剩餘時間
        fast_sec = round(self.fast_timer / 30, 2) if self.fast_timer > 0 else 0
        if not self.fast_used:
            self.info_label.config(text=f'加速剩餘: {fast_sec} 秒   空白鍵啟動加速(僅限一次)')
        else:
            self.info_label.config(text=f'加速已用完')

        self.draw()
        self.master.after(30, self.update)

    def draw(self):
        self.canvas.delete('all')
        # 畫彎道賽道
        for y in range(0, self.height, 4):
            wy = y + self.camera_offset
            road_x = self.get_road_x(wy)
            self.canvas.create_rectangle(road_x, y, road_x + self.road_w, y+4, fill='gray', width=0)
        # 終點線
        fy = self.finish_line - self.camera_offset
        road_x_finish = self.get_road_x(self.finish_line)
        if 0 <= fy <= self.height:
            self.canvas.create_rectangle(road_x_finish, fy, road_x_finish + self.road_w, fy+6, fill='yellow')
            self.canvas.create_text(road_x_finish + 30, fy+18, text='終點', fill='yellow', font=('Arial', 14))
        # 賽道中線
        for y in range(0, self.world_height, 40):
            sy = y - self.camera_offset
            if -20 <= sy <= self.height:
                road_x = self.get_road_x(y)
                self.canvas.create_rectangle(road_x + self.road_w//2 - 5, sy, road_x + self.road_w//2 + 5, sy+20, fill='white', width=0)
        # 玩家車
        x, y = self.car_x, self.car_y - self.camera_offset
        self.canvas.create_rectangle(x - self.car_w//2, y - self.car_h//2, x + self.car_w//2, y + self.car_h//2, fill='blue', outline='black', width=2)
        self.canvas.create_rectangle(x - 12, y - 25, x + 12, y - 5, fill='skyblue', outline='black')
        self.canvas.create_oval(x - self.car_w//2 - 6, y - 20, x - self.car_w//2 + 6, y - 8, fill='black')
        self.canvas.create_oval(x + self.car_w//2 - 6, y - 20, x + self.car_w//2 + 6, y - 8, fill='black')
        self.canvas.create_oval(x - self.car_w//2 - 6, y + 20, x - self.car_w//2 + 6, y + 32, fill='black')
        self.canvas.create_oval(x + self.car_w//2 - 6, y + 20, x + self.car_w//2 + 6, y + 32, fill='black')
        # 對手車
        rx, ry = self.rival_x, self.rival_y - self.camera_offset
        self.canvas.create_rectangle(rx - self.rival_w//2, ry - self.rival_h//2, rx + self.rival_w//2, ry + self.rival_h//2, fill='green', outline='black', width=2)
        self.canvas.create_rectangle(rx - 12, ry - 25, rx + 12, ry - 5, fill='lightgreen', outline='black')
        self.canvas.create_oval(rx - self.rival_w//2 - 6, ry - 20, rx - self.rival_w//2 + 6, ry - 8, fill='black')
        self.canvas.create_oval(rx + self.rival_w//2 - 6, ry - 20, rx + self.rival_w//2 + 6, ry - 8, fill='black')
        self.canvas.create_oval(rx - self.rival_w//2 - 6, ry + 20, rx - self.rival_w//2 + 6, ry + 32, fill='black')
        self.canvas.create_oval(rx + self.rival_w//2 - 6, ry + 20, rx + self.rival_w//2 + 6, ry + 32, fill='black')
        # 障礙車
        for ox, oy, color in self.obstacles:
            sy = oy - self.camera_offset
            if -self.obstacle_h <= sy <= self.height + self.obstacle_h:
                self.canvas.create_rectangle(ox - self.obstacle_w//2, sy - self.obstacle_h//2, ox + self.obstacle_w//2, sy + self.obstacle_h//2, fill=color, outline='black', width=2)
                self.canvas.create_rectangle(ox - 12, sy - 25, ox + 12, sy - 5, fill='pink', outline='black')
                self.canvas.create_oval(ox - self.obstacle_w//2 - 6, sy - 20, ox - self.obstacle_w//2 + 6, sy - 8, fill='black')
                self.canvas.create_oval(ox + self.obstacle_w//2 - 6, sy - 20, ox + self.obstacle_w//2 + 6, sy - 8, fill='black')
                self.canvas.create_oval(ox - self.obstacle_w//2 - 6, sy + 20, ox - self.obstacle_w//2 + 6, sy + 32, fill='black')
                self.canvas.create_oval(ox + self.obstacle_w//2 - 6, sy + 20, ox + self.obstacle_w//2 + 6, sy + 32, fill='black')
        # 顯示勝利者
        if not self.running and self.game_winner:
            self.canvas.create_text(self.width//2, self.height//2, text=f'{self.game_winner}獲勝！', fill='gold', font=('Arial', 32))
            self.canvas.create_text(self.width//2, self.height//2+40, text='按 Enter 重新開始', fill='yellow', font=('Arial', 18))

if __name__ == '__main__':
    root = tk.Tk()
    game = RacingGame(root)
    root.mainloop()


# 簡單賽車遊戲
import tkinter as tk
import random

class RacingGame:
    def __init__(self, master):
        self.master = master
        import tkinter as tk
        import random

        class RacingGame:
            def __init__(self, master):
                self.master = master
                self.master.title('賽車遊戲')
                self.width = 400
                self.height = 600
                self.road_w = 300
                self.road_x = (self.width - self.road_w) // 2
                self.finish_line = 80 * 40  # 終點設更遠
                self.world_height = 600 * 40  # 世界高度也加倍
                self.canvas = tk.Canvas(master, width=self.width, height=self.height, bg='darkgreen')
                self.canvas.pack()
                self.score_label = tk.Label(master, text='', font=('Arial', 14))
                self.score_label.pack()

                # 玩家車
                self.car_w = 40
                self.car_h = 70
                self.car_x = self.width // 2
                self.car_y = self.world_height - 100

                # 對手車
                self.rival_w = 40
                self.rival_h = 70
                self.rival_x = self.width // 2 + 60
                self.rival_y = self.world_height - 100
                self.rival_dir_x = 0
                self.rival_dir_y = 0

                # 速度設定
                self.base_speed = 20
                self.is_fast = False
                self.rival_speed = self.base_speed
                self.player_speed = self.base_speed

                # 障礙車
                self.obstacle_w = 40
                self.obstacle_h = 70
                self.obstacle_speed = 7
                self.obstacles = []  # [(x, y, color)]
                self.max_obstacles = 10

                self.running = True
                self.game_winner = None
                self.camera_offset = 0

                self.pressed_keys = set()
                self.master.bind('<KeyPress>', self.on_key_press)
                self.master.bind('<KeyRelease>', self.on_key_release)
                self.master.bind('<Return>', self.restart_game)
                self.update()

            def on_key_press(self, event):
                self.pressed_keys.add(event.keysym)
                if event.keysym in ('Shift_L', 'Shift_R'):
                    self.is_fast = True

            def on_key_release(self, event):
                if event.keysym in self.pressed_keys:
                    self.pressed_keys.remove(event.keysym)
                if event.keysym in ('Shift_L', 'Shift_R'):
                    self.is_fast = False

            def move_player(self):
                move = self.base_speed * (2 if self.is_fast else 1)
                dx = dy = 0
                if 'Left' in self.pressed_keys and self.car_x - self.car_w//2 > self.road_x:
                    dx -= move
                if 'Right' in self.pressed_keys and self.car_x + self.car_w//2 < self.road_x + self.road_w:
                    dx += move
                if 'Up' in self.pressed_keys and self.car_y - self.car_h//2 > 0:
                    dy -= move
                if 'Down' in self.pressed_keys and self.car_y + self.car_h//2 < self.world_height:
                    dy += move
                self.car_x += dx
                self.car_y += dy

            def shift_down(self, event):
                self.is_fast = True

            def shift_up(self, event):
                self.is_fast = False

            def restart_game(self, event):
                if not self.running:
                    self.car_x = self.width // 2
                    self.car_y = self.world_height - 100
                    self.rival_x = self.width // 2 + 60
                    self.rival_y = self.world_height - 100
                    self.obstacles = []
                    self.running = True
                    self.game_winner = None
                    self.update()

            def spawn_obstacle(self):
                x = random.randint(self.road_x + self.obstacle_w//2, self.road_x + self.road_w - self.obstacle_w//2)
                y = random.randint(0, self.world_height - 200)
                color = random.choice(['red', 'orange', 'purple', 'brown', 'gray'])
                self.obstacles.append([x, y, color])

            def update(self):
                if not self.running:
                    self.draw()
                    return
                # 障礙車數量維持
                while len(self.obstacles) < self.max_obstacles:
                    self.spawn_obstacle()

                # 玩家移動（可同時多方向）
                self.move_player()

                # 玩家與障礙車碰撞
                for obs in self.obstacles:
                    if (abs(obs[0] - self.car_x) < (self.obstacle_w + self.car_w)//2) and (abs(obs[1] - self.car_y) < (self.obstacle_h + self.car_h)//2):
                        # 撞到障礙車，彈開
                        if self.car_y > obs[1]:
                            self.car_y = min(self.world_height - self.car_h//2, self.car_y + 40)
                        else:
                            self.car_y = max(self.car_h//2, self.car_y - 40)
                # 對手與障礙車碰撞
                for obs in self.obstacles:
                    if (abs(obs[0] - self.rival_x) < (self.obstacle_w + self.rival_w)//2) and (abs(obs[1] - self.rival_y) < (self.obstacle_h + self.rival_h)//2):
                        if self.rival_y > obs[1]:
                            self.rival_y = min(self.world_height - self.rival_h//2, self.rival_y + 40)
                        else:
                            self.rival_y = max(self.rival_h//2, self.rival_y - 40)
                # 玩家與對手車碰撞
                if (abs(self.car_x - self.rival_x) < (self.car_w + self.rival_w)//2) and (abs(self.car_y - self.rival_y) < (self.car_h + self.rival_h)//2):
                    if self.car_y < self.rival_y:
                        self.car_y = max(self.car_h//2, self.car_y - 40)
                        self.rival_y = min(self.world_height - self.rival_h//2, self.rival_y + 40)
                    else:
                        self.car_y = min(self.world_height - self.car_h//2, self.car_y + 40)
                        self.rival_y = max(self.rival_h//2, self.rival_y - 40)
                    if self.car_x < self.rival_x:
                        self.car_x = max(self.road_x + self.car_w//2, self.car_x - 40)
                        self.rival_x = min(self.road_x + self.road_w - self.rival_w//2, self.rival_x + 40)
                    else:
                        self.car_x = min(self.road_x + self.road_w - self.car_w//2, self.car_x + 40)
                        self.rival_x = max(self.road_x + self.rival_w//2, self.rival_x - 40)
                # 對手 AI 控制（自動往終點，偶爾閃避障礙）
                self.rival_dir_x = 0
                self.rival_dir_y = -1
                # 若前方有障礙，隨機左右閃避
                for obs in self.obstacles:
                    if abs(obs[1] - (self.rival_y - self.rival_h//2)) < 60 and abs(obs[0] - self.rival_x) < self.rival_w:
                        self.rival_dir_x = random.choice([-1, 1])
                        break
                # 移動對手車
                move = self.base_speed * (2 if random.random() < 0.1 else 1)
                if self.rival_x - self.rival_w//2 > self.road_x and self.rival_dir_x == -1:
                    self.rival_x -= move
                if self.rival_x + self.rival_w//2 < self.road_x + self.road_w and self.rival_dir_x == 1:
                    self.rival_x += move
                if self.rival_y - self.rival_h//2 > 0 and self.rival_dir_y == -1:
                    self.rival_y -= self.base_speed
                if self.rival_y + self.rival_h//2 < self.world_height and self.rival_dir_y == 1:
                    self.rival_y += self.base_speed
                # 終點判斷
                if self.car_y - self.car_h//2 <= self.finish_line:
                    self.running = False
                    self.game_winner = '玩家'
                elif self.rival_y - self.rival_h//2 <= self.finish_line:
                    self.running = False
                    self.game_winner = '對手'
                # 畫面跟隨玩家
                self.camera_offset = self.car_y - self.height // 2
                self.camera_offset = max(0, min(self.camera_offset, self.world_height - self.height))
                self.draw()
                self.master.after(30, self.update)

            def draw(self):
                self.canvas.delete('all')
                # 賽道
                self.canvas.create_rectangle(self.road_x, 0, self.road_x + self.road_w, self.height, fill='gray')
                # 終點線
                fy = self.finish_line - self.camera_offset
                if 0 <= fy <= self.height:
                    self.canvas.create_rectangle(self.road_x, fy, self.road_x + self.road_w, fy+6, fill='yellow')
                    self.canvas.create_text(self.road_x + 30, fy+18, text='終點', fill='yellow', font=('Arial', 14))
                # 賽道中線
                for y in range(0, self.world_height, 40):
                    sy = y - self.camera_offset
                    if -20 <= sy <= self.height:
                        self.canvas.create_rectangle(self.width//2 - 5, sy, self.width//2 + 5, sy+20, fill='white', width=0)
                # 玩家車
                x, y = self.car_x, self.car_y - self.camera_offset
                self.canvas.create_rectangle(x - self.car_w//2, y - self.car_h//2, x + self.car_w//2, y + self.car_h//2, fill='blue', outline='black', width=2)
                self.canvas.create_rectangle(x - 12, y - 25, x + 12, y - 5, fill='skyblue', outline='black')
                self.canvas.create_oval(x - self.car_w//2 - 6, y - 20, x - self.car_w//2 + 6, y - 8, fill='black')
                self.canvas.create_oval(x + self.car_w//2 - 6, y - 20, x + self.car_w//2 + 6, y - 8, fill='black')
                self.canvas.create_oval(x - self.car_w//2 - 6, y + 20, x - self.car_w//2 + 6, y + 32, fill='black')
                self.canvas.create_oval(x + self.car_w//2 - 6, y + 20, x + self.car_w//2 + 6, y + 32, fill='black')
                # 對手車
                rx, ry = self.rival_x, self.rival_y - self.camera_offset
                self.canvas.create_rectangle(rx - self.rival_w//2, ry - self.rival_h//2, rx + self.rival_w//2, ry + self.rival_h//2, fill='green', outline='black', width=2)
                self.canvas.create_rectangle(rx - 12, ry - 25, rx + 12, ry - 5, fill='lightgreen', outline='black')
                self.canvas.create_oval(rx - self.rival_w//2 - 6, ry - 20, rx - self.rival_w//2 + 6, ry - 8, fill='black')
                self.canvas.create_oval(rx + self.rival_w//2 - 6, ry - 20, rx + self.rival_w//2 + 6, ry - 8, fill='black')
                self.canvas.create_oval(rx - self.rival_w//2 - 6, ry + 20, rx - self.rival_w//2 + 6, ry + 32, fill='black')
                self.canvas.create_oval(rx + self.rival_w//2 - 6, ry + 20, rx + self.rival_w//2 + 6, ry + 32, fill='black')
                # 障礙車
                for ox, oy, color in self.obstacles:
                    sy = oy - self.camera_offset
                    if -self.obstacle_h <= sy <= self.height + self.obstacle_h:
                        self.canvas.create_rectangle(ox - self.obstacle_w//2, sy - self.obstacle_h//2, ox + self.obstacle_w//2, sy + self.obstacle_h//2, fill=color, outline='black', width=2)
                        self.canvas.create_rectangle(ox - 12, sy - 25, ox + 12, sy - 5, fill='pink', outline='black')
                        self.canvas.create_oval(ox - self.obstacle_w//2 - 6, sy - 20, ox - self.obstacle_w//2 + 6, sy - 8, fill='black')
                        self.canvas.create_oval(ox + self.obstacle_w//2 - 6, sy - 20, ox + self.obstacle_w//2 + 6, sy - 8, fill='black')
                        self.canvas.create_oval(ox - self.obstacle_w//2 - 6, sy + 20, ox - self.obstacle_w//2 + 6, sy + 32, fill='black')
                        self.canvas.create_oval(ox + self.obstacle_w//2 - 6, sy + 20, ox + self.obstacle_w//2 + 6, sy + 32, fill='black')
                # 顯示勝利者
                if not self.running and self.game_winner:
                    self.canvas.create_text(self.width//2, self.height//2, text=f'{self.game_winner}獲勝！', fill='gold', font=('Arial', 32))
                    self.canvas.create_text(self.width//2, self.height//2+40, text='按 Enter 重新開始', fill='yellow', font=('Arial', 18))

        if __name__ == '__main__':
            root = tk.Tk()
            game = RacingGame(root)
            root.mainloop()
    def move_down(self, event):
        speed = self.vertical_speed
        if self.player_slow_timer > 0:
            speed = int(self.vertical_speed * self.slow_factor)
        if self.car_y + self.car_h//2 < self.world_height:
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
        # 隨機選擇顏色
        color = random.choice(['red', 'orange', 'purple', 'brown', 'gray'])
        self.obstacles.append([x, -self.obstacle_h, color])

    def update(self):
        if not self.running:
            self.canvas.create_text(self.width//2, self.height//2, text='遊戲結束', fill='white', font=('Arial', 32))
            self.canvas.create_text(self.width//2, self.height//2+40, text='按 Enter 重新開始', fill='yellow', font=('Arial', 18))
            return
        # 移動障礙物
        for obs in self.obstacles:
            obs[1] += self.obstacle_speed
        # 移除超出世界範圍的障礙物
        self.obstacles = [obs for obs in self.obstacles if obs[1] < self.world_height]
        # 檢查玩家車碰撞障礙物
        for obs in self.obstacles:
            if (abs(obs[0] - self.car_x) < (self.obstacle_w + self.car_w)//2) and (abs(obs[1] - self.car_y) < (self.obstacle_h + self.car_h)//2):
                # 玩家車撞到障礙物，彈開
                if self.car_y > obs[1]:
                    self.car_y = min(self.world_height - self.car_h//2, self.car_y + 40)
                else:
                    self.car_y = max(self.car_h//2, self.car_y - 40)

        # 檢查對手車碰撞障礙物
        for obs in self.obstacles:
            if (abs(obs[0] - self.rival_x) < (self.obstacle_w + self.rival_w)//2) and (abs(obs[1] - self.rival_y) < (self.obstacle_h + self.rival_h)//2):
                # 對手車撞到障礙物，彈開
                if self.rival_y > obs[1]:
                    self.rival_y = min(self.world_height - self.rival_h//2, self.rival_y + 40)
                else:
                    self.rival_y = max(self.rival_h//2, self.rival_y - 40)

        # 對手車隨機左右與前後移動
        # 對手車自動穩定往終點前進
        self.rival_move_counter += 1
        # 讓對手車主要往上（終點），偶爾左右微調
        if self.rival_move_counter % 20 == 0:
            self.rival_dir_x = random.choice([-1, 0, 1])
        self.rival_dir_y = -1  # 一直往上
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
        elif self.rival_x + self.rival_w//2 > self.road_x + self.road_w:
            self.rival_x = self.road_x + self.road_w - self.rival_w//2
        if self.rival_y - self.rival_h//2 < 0:
            self.rival_y = self.rival_h//2
        elif self.rival_y + self.rival_h//2 > self.world_height:
            self.rival_y = self.world_height - self.rival_h//2

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

        # 產生新障礙物（機率提高）
        for _ in range(2):
            if random.random() < 0.06:
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

        # 計算畫面偏移量，讓玩家車盡量在畫面中央
        self.camera_offset = self.car_y - self.height // 2
        self.camera_offset = max(0, min(self.camera_offset, self.world_height - self.height))

        self.draw()
        self.master.after(30, self.update)

    def draw(self):
        self.canvas.delete('all')
        # 畫賽道
        self.canvas.create_rectangle(self.road_x, 0, self.road_x + self.road_w, self.height, fill='gray')
        # 畫終點線（根據 camera_offset 調整）
        fy = self.finish_line - self.camera_offset
        if 0 <= fy <= self.height:
            self.canvas.create_rectangle(self.road_x, fy, self.road_x + self.road_w, fy+6, fill='yellow')
            self.canvas.create_text(self.road_x + 30, fy+18, text='終點', fill='yellow', font=('Arial', 14))
        # 畫賽道中線
        for y in range(0, self.world_height, 40):
            sy = y - self.camera_offset
            if -20 <= sy <= self.height:
                self.canvas.create_rectangle(self.width//2 - 5, sy, self.width//2 + 5, sy+20, fill='white', width=0)
        # 畫玩家車子（藍色）
        x, y = self.car_x, self.car_y - self.camera_offset
        self.canvas.create_rectangle(x - self.car_w//2, y - self.car_h//2, x + self.car_w//2, y + self.car_h//2, fill='blue', outline='black', width=2)
        self.canvas.create_rectangle(x - 12, y - 25, x + 12, y - 5, fill='skyblue', outline='black')  # 車窗
        self.canvas.create_oval(x - self.car_w//2 - 6, y - 20, x - self.car_w//2 + 6, y - 8, fill='black')  # 左輪
        self.canvas.create_oval(x + self.car_w//2 - 6, y - 20, x + self.car_w//2 + 6, y - 8, fill='black')  # 右輪
        self.canvas.create_oval(x - self.car_w//2 - 6, y + 20, x - self.car_w//2 + 6, y + 32, fill='black')  # 左輪
        self.canvas.create_oval(x + self.car_w//2 - 6, y + 20, x + self.car_w//2 + 6, y + 32, fill='black')  # 右輪
        # 畫對手車（綠色）
        rx, ry = self.rival_x, self.rival_y - self.camera_offset
        self.canvas.create_rectangle(rx - self.rival_w//2, ry - self.rival_h//2, rx + self.rival_w//2, ry + self.rival_h//2, fill='green', outline='black', width=2)
        self.canvas.create_rectangle(rx - 12, ry - 25, rx + 12, ry - 5, fill='lightgreen', outline='black')
        self.canvas.create_oval(rx - self.rival_w//2 - 6, ry - 20, rx - self.rival_w//2 + 6, ry - 8, fill='black')
        self.canvas.create_oval(rx + self.rival_w//2 - 6, ry - 20, rx + self.rival_w//2 + 6, ry - 8, fill='black')
        self.canvas.create_oval(rx - self.rival_w//2 - 6, ry + 20, rx - self.rival_w//2 + 6, ry + 32, fill='black')
        self.canvas.create_oval(rx + self.rival_w//2 - 6, ry + 20, rx + self.rival_w//2 + 6, ry + 32, fill='black')
        # 畫障礙物（多色車型）
        for ox, oy, color in self.obstacles:
            sy = oy - self.camera_offset
            if -self.obstacle_h <= sy <= self.height + self.obstacle_h:
                self.canvas.create_rectangle(ox - self.obstacle_w//2, sy - self.obstacle_h//2, ox + self.obstacle_w//2, sy + self.obstacle_h//2, fill=color, outline='black', width=2)
                self.canvas.create_rectangle(ox - 12, sy - 25, ox + 12, sy - 5, fill='pink', outline='black')
                self.canvas.create_oval(ox - self.obstacle_w//2 - 6, sy - 20, ox - self.obstacle_w//2 + 6, sy - 8, fill='black')
                self.canvas.create_oval(ox + self.obstacle_w//2 - 6, sy - 20, ox + self.obstacle_w//2 + 6, sy - 8, fill='black')
                self.canvas.create_oval(ox - self.obstacle_w//2 - 6, sy + 20, ox - self.obstacle_w//2 + 6, sy + 32, fill='black')
                self.canvas.create_oval(ox + self.obstacle_w//2 - 6, sy + 20, ox + self.obstacle_w//2 + 6, sy + 32, fill='black')

        # 顯示勝利者
        if not self.running and self.game_winner:
            self.canvas.create_text(self.width//2, self.height//2, text=f'{self.game_winner}獲勝！', fill='gold', font=('Arial', 32))
            self.canvas.create_text(self.width//2, self.height//2+40, text='按 Enter 重新開始', fill='yellow', font=('Arial', 18))

if __name__ == '__main__':
    root = tk.Tk()
    game = RacingGame(root)
    root.mainloop()
