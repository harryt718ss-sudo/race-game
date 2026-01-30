import sys
import random
import math
import time
from dataclasses import dataclass

print("Checking environment...")
try:
    import pygame
except ImportError as e:
    print(f"Error: Missing pygame. Please run 'pip install pygame'")
    sys.exit()

# --- 遊戲設定 ---
WIDTH, HEIGHT = 800, 600
ROAD_WIDTH = 500      
FINISH_DIST = 80000   # 距離拉長，讓速度差距造成的壓力更明顯

# --- 玩家設定 (保持操控感) ---
P_BASE = 75           
P_BOOST = 130         
P_OFFROAD = 30        
STEER_SPEED = 600     

# ★★★ 對手增強設定 (BOSS 級) ★★★
E_BASE = 80           # 它的基礎極速比你快 (你 75 vs 他 80)
                      # 這意味著直線跑久了你一定會輸，必須靠彎道或氮氣

# 遊戲狀態
STATE_COUNTDOWN = 0
STATE_RACING = 1
STATE_GAMEOVER = 2

@dataclass
class Car:
    x: float
    y: float
    color: tuple
    lane_offset: float = 0.0

class HardcoreRacing:
    def __init__(self):
        print("Initializing Hardcore Mode...")
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Racing: HARDCORE CHALLENGE")
        self.clock = pygame.time.Clock()
        
        try:
            self.font = pygame.font.SysFont("arial", 22, bold=True)
            self.big_font = pygame.font.SysFont("arial", 80, bold=True)
            self.huge_font = pygame.font.SysFont("arial", 120, bold=True)
            self.arrow_font = pygame.font.SysFont("monospace", 100, bold=True)
        except:
            self.font = pygame.font.Font(None, 22)
            self.big_font = pygame.font.Font(None, 80)
            self.huge_font = pygame.font.Font(None, 120)
            self.arrow_font = pygame.font.Font(None, 100)

        self.player = Car(WIDTH/2, 0.0, (0, 150, 255))
        # 對手改為黑色，看起來更殺
        self.enemy = Car(WIDTH/2 + 120, 0.0, (40, 40, 40), lane_offset=120)
        
        self.road_map = [] 
        self.generate_track() 

        self.can_boost = True
        self.is_boosting = False
        self.boost_time = 0.0
        
        self.state = STATE_COUNTDOWN
        self.start_timestamp = time.time() 
        self.winner = None 
        self.blink_timer = 0
        
        self.running = True

    def generate_track(self):
        print("Generating technical track...")
        current_x = WIDTH / 2
        current_angle = 0.0 
        y = 0
        
        # 起跑直線
        for _ in range(2000):
            self.road_map.append(current_x)
            y += 1
            
        loop_guard = 0
        while y < FINISH_DIST + HEIGHT + 2000:
            loop_guard += 1
            if loop_guard > 200000: break

            segment_style = random.choices(
                ["STRAIGHT", "CURVE_LEFT", "CURVE_RIGHT"],
                weights=[50, 25, 25] # 彎道稍微多一點點
            )[0]

            if current_x < 200: segment_style = "CURVE_RIGHT"
            elif current_x > WIDTH + 200: segment_style = "CURVE_LEFT"

            length = random.randint(2000, 5000) 
            angle_target = 0.0 

            if segment_style == "STRAIGHT": angle_target = 0.0
            elif segment_style == "CURVE_LEFT": angle_target = -0.3 
            elif segment_style == "CURVE_RIGHT": angle_target = 0.3

            for i in range(length):
                diff = angle_target - current_angle
                current_angle += diff * 0.001 
                current_x += current_angle * 0.8
                self.road_map.append(current_x)
                y += 1
                if y >= FINISH_DIST + HEIGHT + 2000: break

    def get_road_center(self, y):
        index = int(y)
        if index < 0: return WIDTH / 2
        if index >= len(self.road_map): return self.road_map[-1]
        return self.road_map[index]

    def update(self):
        dt = self.clock.tick(60) / 1000.0
        if dt > 0.1: dt = 0.1 
        current_time = time.time()
        self.blink_timer += dt * 5

        if self.state == STATE_COUNTDOWN:
            elapsed = current_time - self.start_timestamp
            if elapsed >= 3.5: self.state = STATE_RACING
            return 

        if self.state == STATE_GAMEOVER: return 

        # --- 玩家操控 ---
        keys = pygame.key.get_pressed()
        move_dist = STEER_SPEED * dt
        
        if keys[pygame.K_LEFT]:  self.player.x -= move_dist
        if keys[pygame.K_RIGHT]: self.player.x += move_dist

        current_road_x = self.get_road_center(self.player.y)
        limit_offset = (ROAD_WIDTH / 2) + 20 
        
        if self.player.x < current_road_x - limit_offset: self.player.x = current_road_x - limit_offset
        elif self.player.x > current_road_x + limit_offset - 46: self.player.x = current_road_x + limit_offset - 46
        
        road_left = current_road_x - (ROAD_WIDTH / 2)
        road_right = current_road_x + (ROAD_WIDTH / 2)
        player_offroad = self.player.x < (road_left - 10) or (self.player.x + 46) > (road_right + 10)

        if self.is_boosting:
            spd = P_BOOST if current_time - self.boost_time < 3.0 else P_BASE
            if spd == P_BASE: self.is_boosting = False
        else:
            spd = P_OFFROAD if player_offroad else P_BASE

        self.player.y += spd * dt * 45

        # --- 對手 AI (強敵邏輯) ---
        enemy_center = self.get_road_center(self.enemy.y)
        target_x = enemy_center + self.enemy.lane_offset
        
        # 它的反應速度變快了
        self.enemy.x += (target_x - self.enemy.x) * 3.5 * dt
        
        enemy_offroad = self.enemy.x < (enemy_center - ROAD_WIDTH/2 - 10) or \
                        (self.enemy.x + 46) > (enemy_center + ROAD_WIDTH/2 + 10)
        
        if enemy_offroad:
            current_e_speed = P_OFFROAD
        else:
            # ★ 惡夢級橡皮筋機制
            dist_diff = self.enemy.y - self.player.y
            
            if dist_diff < -200: 
                # 落後一點點：立刻開外掛加速 (1.5倍)
                current_e_speed = E_BASE * 1.5
            elif dist_diff < 50:
                # 緊貼在你後面：保持超車優勢 (1.2倍)
                current_e_speed = E_BASE * 1.2
            elif dist_diff > 600:
                # 領先非常多：稍微減速一點點防止消失，但依然很快
                current_e_speed = E_BASE * 0.95
            else:
                # 領先狀態：保持全速 (1.05倍)，試圖甩開你
                current_e_speed = E_BASE * 1.05

        self.enemy.y += current_e_speed * dt * 45
        
        # 頻繁切換車道 (更加躁動)
        if random.random() < 0.02: # 提高頻率
            self.enemy.lane_offset = random.choice([-150, 0, 150])

        # 勝負判定
        if self.player.y >= FINISH_DIST:
            self.state = STATE_GAMEOVER
            self.winner = "PLAYER"
        elif self.enemy.y >= FINISH_DIST:
            self.state = STATE_GAMEOVER
            self.winner = "ENEMY"

    def draw_turn_assist(self):
        look_ahead = 700 
        current_x = self.get_road_center(self.player.y)
        future_x = self.get_road_center(self.player.y + look_ahead)
        diff = future_x - current_x
        THRESHOLD = 100
        
        if abs(diff) > THRESHOLD:
            direction = ">>>" if diff > 0 else "<<<"
            if abs(diff) > 300:
                base_color = (255, 50, 50) 
                scale = 1.2
            else:
                base_color = (255, 220, 0) 
                scale = 1.0
                
            text_surf = self.arrow_font.render(direction, True, base_color)
            if scale != 1.0:
                w = int(text_surf.get_width() * scale)
                h = int(text_surf.get_height() * scale)
                text_surf = pygame.transform.scale(text_surf, (w, h))

            dest_rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
            shadow_surf = self.arrow_font.render(direction, True, (0,0,0))
            if scale != 1.0:
                 shadow_surf = pygame.transform.scale(shadow_surf, (int(shadow_surf.get_width()*scale), int(shadow_surf.get_height()*scale)))
            shadow_rect = shadow_surf.get_rect(center=(WIDTH//2 + 3, HEIGHT//2 - 97))
            
            self.screen.blit(shadow_surf, shadow_rect)
            self.screen.blit(text_surf, dest_rect)

    def draw(self):
        self.screen.fill((100, 160, 220)) 
        pygame.draw.rect(self.screen, (34, 139, 34), (0, HEIGHT/2, WIDTH, HEIGHT/2)) 

        camera_x = self.player.x - (WIDTH / 2)
        slice_height = 4
        view_height = HEIGHT 
        
        for i in range(0, view_height, slice_height):
            world_y = self.player.y + (view_height - i)
            world_center_x = self.get_road_center(world_y)
            screen_draw_x = world_center_x - camera_x
            
            segment_idx = int(world_y) // 200
            is_dark = segment_idx % 2 == 0
            
            grass_col = (34, 139, 34) if is_dark else (0, 100, 0)
            road_col = (100, 100, 100) if is_dark else (110, 110, 110)
            curb_col = (255, 255, 255) if (int(world_y)//100)%2==0 else (200, 0, 0)
            
            draw_y = i
            
            pygame.draw.rect(self.screen, grass_col, (0, draw_y, WIDTH, slice_height))
            pygame.draw.rect(self.screen, curb_col, (screen_draw_x - ROAD_WIDTH/2 - 15, draw_y, ROAD_WIDTH + 30, slice_height))
            pygame.draw.rect(self.screen, road_col, (screen_draw_x - ROAD_WIDTH/2, draw_y, ROAD_WIDTH, slice_height))
            
            pygame.draw.rect(self.screen, (255, 255, 255), (screen_draw_x - ROAD_WIDTH/4, draw_y, 4, slice_height))
            pygame.draw.rect(self.screen, (255, 255, 255), (screen_draw_x + ROAD_WIDTH/4, draw_y, 4, slice_height))
            if (int(world_y) // 100) % 2 == 0:
                 pygame.draw.rect(self.screen, (255, 255, 255), (screen_draw_x, draw_y, 4, slice_height))

        # 車輛
        enemy_screen_y = HEIGHT - 200 - (self.enemy.y - self.player.y)
        enemy_screen_x = self.enemy.x - camera_x
        if -100 < enemy_screen_y < HEIGHT:
            pygame.draw.rect(self.screen, self.enemy.color, (int(enemy_screen_x), int(enemy_screen_y), 46, 70))
            # 兇猛的紅色車尾燈
            pygame.draw.rect(self.screen, (255, 0, 0), (int(enemy_screen_x)+5, int(enemy_screen_y)+5, 12, 6))
            pygame.draw.rect(self.screen, (255, 0, 0), (int(enemy_screen_x)+29, int(enemy_screen_y)+5, 12, 6))
            
        player_draw_x = WIDTH / 2 - 23
        pygame.draw.rect(self.screen, self.player.color, (int(player_draw_x), HEIGHT - 200, 46, 70))
        # 玩家車燈
        pygame.draw.rect(self.screen, (200, 0, 0), (int(player_draw_x)+5, HEIGHT - 135, 10, 5))
        pygame.draw.rect(self.screen, (200, 0, 0), (int(player_draw_x)+31, HEIGHT - 135, 10, 5))
        
        if self.is_boosting:
             pygame.draw.rect(self.screen, (255, 200, 0), (int(player_draw_x)+10, HEIGHT - 130, 26, 20))

        # UI
        prog = min(100, int(self.player.y / FINISH_DIST * 100))
        pygame.draw.rect(self.screen, (0,0,0), (0,0,WIDTH, 60))
        self.screen.blit(self.font.render(f"DIST: {prog}%", True, (255,255,255)), (20, 20))
        
        if self.can_boost and self.state == STATE_RACING:
            self.screen.blit(self.font.render("NITRO [SPACE]", True, (0, 255, 255)), (WIDTH - 200, 20))

        self.draw_turn_assist()

        if self.state == STATE_COUNTDOWN:
            elapsed = time.time() - self.start_timestamp
            remain = 3 - int(elapsed)
            s = pygame.Surface((WIDTH, HEIGHT))
            s.set_alpha(100)
            s.fill((0,0,0))
            self.screen.blit(s, (0,0))
            if remain > 0:
                txt = self.huge_font.render(str(remain), True, (255, 0, 0))
            else:
                txt = self.huge_font.render("GO!", True, (0, 255, 0))
            self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 100))

        elif self.state == STATE_GAMEOVER:
            s = pygame.Surface((WIDTH, HEIGHT))
            s.set_alpha(150)
            s.fill((0,0,0))
            self.screen.blit(s, (0,0))
            if self.winner == "PLAYER":
                msg, col = "INCREDIBLE WIN!", (0, 255, 0)
            else:
                msg, col = "DEFEATED", (255, 0, 0)
            txt = self.huge_font.render(msg, True, col)
            self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 50))
            sub = self.font.render("Press ESC to Exit", True, (255,255,255))
            self.screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 80))

        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: self.running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE: self.running = False
                        if event.key == pygame.K_SPACE and self.state == STATE_RACING:
                            if self.can_boost:
                                self.is_boosting = True
                                self.can_boost = False
                                self.boost_time = time.time()
                self.update()
                self.draw()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            pygame.quit()

if __name__ == "__main__":
    HardcoreRacing().run()