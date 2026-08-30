import tkinter as tk 
import time
import random
import math
 
# ==========================================
# 模块 2: 输入管理模块 (Input Manager)
# ==========================================
class InputManager:
    def __init__(self, root, game_engine):
        self.pressed_keys = set()
        self.game_engine = game_engine
        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)
 
    def on_key_press(self, event):
        key = event.keysym.lower()
        if key == "space":
            self.game_engine.toggle_pause()
        else:
            self.pressed_keys.add(key)
 
    def on_key_release(self, event):
        key = event.keysym.lower()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
 
    def is_pressed(self, key):
        return key in self.pressed_keys 
 
# ==========================================
# 模块 3: 物理与碰撞检测模块 (Physics & Collision)
# ==========================================
class Physics:
    GRAVITY = 0.8 
    GROUND_Y = 450 
 
    @staticmethod 
    def apply_gravity_and_ground(entity):
        entity.vy += Physics.GRAVITY
        entity.y += entity.vy
        if entity.y + entity.height >= Physics.GROUND_Y:
            entity.y = Physics.GROUND_Y - entity.height
            entity.vy = 0
            entity.on_ground = True
        else:
            entity.on_ground = False
 
class Collision:
    @staticmethod 
    def check_aabb(rect1, rect2):
        x1, y1, w1, h1 = rect1 
        x2, y2, w2, h2 = rect2 
        return (x1 < x2 + w2 and x1 + w1 > x2 and
                y1 < y2 + h2 and y1 + h1 > y2)
 
# ==========================================
# 模块 6 (前置): 子弹模块 (Projectile)
# ==========================================
class Projectile:
    def __init__(self, x, y, direction):
        self.x = x 
        self.y = y 
        self.width = 10
        self.height = 4
        self.speed = 12 * direction
        self.active = True
        self.canvas_id = None 
 
    def update(self):
        self.x += self.speed
 
    def get_rect(self):
        return (self.x, self.y, self.width, self.height)
 
    def render(self, canvas):
        if self.canvas_id:
            for cid in self.canvas_id:
                canvas.delete(cid)
        core = canvas.create_oval(self.x, self.y, self.x + self.width,
                                  self.y + self.height,
                                  fill="#f1c40f", outline="")
        tail_x = self.x - 6 if self.speed > 0 else self.x + self.width
        tail = canvas.create_oval(tail_x, self.y - 1, tail_x + 6,
                                  self.y + self.height + 1,
                                  fill="#f39c12", outline="")
        self.canvas_id = [core, tail]
 
    def destroy(self, canvas):
        self.active = False
        if self.canvas_id is not None:
            if isinstance(self.canvas_id, list):
                for cid in self.canvas_id:
                    canvas.delete(cid)
            else:
                canvas.delete(self.canvas_id)
            self.canvas_id = None
 
# ==========================================
# 模块 4: 玩家实体模块 (Player Class)
# ==========================================
class Player:
    def __init__(self, x, y):
        self.x = x 
        self.y = y 
        self.width = 30
        self.height = 40
        self.vx = 0
        self.vy = 0
        self.speed = 5
        self.jump_power = -13
        self.hp = 3
        self.max_hp = 3
 
        self.on_ground = False
        self.jump_count = 0 
        self.max_jumps = 2
        self.k_held = False
 
        self.facing_right = True
        self.attack_cooldown = 0
        self.attack_delay = 30 
 
        self.invincible_time = 0
        self.invincible_duration = 100
        self.canvas_id = None
 
    def update(self, input_manager, physics, screen_width):
        self.vx = 0
        if input_manager.is_pressed('a'):
            self.vx = -self.speed
            self.facing_right = False
        if input_manager.is_pressed('d'):
            self.vx = self.speed
            self.facing_right = True
 
        self.x += self.vx
        if self.x < 0:
            self.x = 0
        if self.x + self.width > screen_width:
            self.x = screen_width - self.width
 
        physics.apply_gravity_and_ground(self)
        if self.on_ground:
            self.jump_count = 0
 
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.invincible_time > 0:
            self.invincible_time -= 1
 
    def handle_jump(self, input_manager):
        if input_manager.is_pressed('k'):
            if not self.k_held:
                if self.jump_count < self.max_jumps:
                    self.vy = self.jump_power
                    self.jump_count += 1
                    self.on_ground = False
                self.k_held = True
        else:
            self.k_held = False 
 
    def attack(self):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = self.attack_delay
            direction = 1 if self.facing_right else -1 
            bullet_x = self.x + self.width if self.facing_right else self.x - 10
            bullet_y = self.y + self.height // 2
            return Projectile(bullet_x, bullet_y, direction)
        return None
 
    def take_damage(self):
        if self.invincible_time <= 0:
            self.hp -= 1
            self.invincible_time = self.invincible_duration
            return True
        return False
 
    def get_rect(self):
        return (self.x, self.y, self.width, self.height)
 
    def render(self, canvas):
        if self.canvas_id:
            for cid in self.canvas_id:
                canvas.delete(cid)
 
        blink = self.invincible_time > 0 and (self.invincible_time // 4) % 2 == 0
        if blink:
            body_color = "#ecf0f1"; outline_color = "#bdc3c7"
        else:
            body_color = "#3498db"; outline_color = "#1abc9c"
 
        body = canvas.create_rectangle(self.x, self.y,
                                       self.x + self.width, self.y + self.height,
                                       fill=body_color, outline=outline_color, width=2)
 
        head_r = 10
        head_cx = self.x + self.width // 2
        head_cy = self.y + head_r
        head = canvas.create_oval(head_cx - head_r, head_cy - head_r,
                                  head_cx + head_r, head_cy + head_r,
                                  fill="#f5cba7", outline="#d4ac0d", width=2)
 
        eye_r = 2
        if self.facing_right:
            e1x, e2x = head_cx + 1, head_cx + 5
        else:
            e1x, e2x = head_cx - 5, head_cx - 1
        eye1 = canvas.create_oval(e1x - eye_r, head_cy - 2,
                                  e1x + eye_r, head_cy + 2,
                                  fill="#2c3e50", outline="")
        eye2 = canvas.create_oval(e2x - eye_r, head_cy + 1,
                                  e2x + eye_r, head_cy + 5,
                                  fill="#2c3e50", outline="")
        mouth = canvas.create_rectangle(head_cx - 3, head_cy + 5,
                                        head_cx + 3, head_cy + 6,
                                        fill="#c0392b", outline="")
 
        neck_y = self.y + head_r * 2
        collar = canvas.create_polygon(
            head_cx - 6, neck_y, head_cx + 6, neck_y,
            head_cx + 3, neck_y + 5, head_cx - 3, neck_y + 5,
            fill="#2980b9", outline=""
        )
 
        belt_y = self.y + self.height * 3 // 5
        belt = canvas.create_rectangle(self.x + 2, belt_y,
                                       self.x + self.width - 2, belt_y + 3,
                                       fill="#7d3c0f", outline="#5d2e0c")
        buckle = canvas.create_rectangle(head_cx - 2, belt_y,
                                         head_cx + 2, belt_y + 3,
                                         fill="#f1c40f", outline="")
 
        leg_color = "#2c3e50" if self.on_ground else "#1a252f"
        leg1 = canvas.create_rectangle(self.x + 4, self.y + self.height - 8,
                                       self.x + 13, self.y + self.height,
                                       fill=leg_color, outline="")
        leg2 = canvas.create_rectangle(self.x + self.width - 13, self.y + self.height - 8,
                                       self.x + self.width - 4, self.y + self.height,
                                       fill=leg_color, outline="")
 
        shoe1 = canvas.create_rectangle(self.x + 3, self.y + self.height - 3,
                                        self.x + 14, self.y + self.height,
                                        fill="#f39c12", outline="#d68910")
        shoe2 = canvas.create_rectangle(self.x + self.width - 14, self.y + self.height - 3,
                                        self.x + self.width - 3, self.y + self.height,
                                        fill="#f39c12", outline="#d68910")
 
        gun_y = self.y + self.height // 2 - 2
        if self.facing_right:
            gun_body = canvas.create_rectangle(self.x + self.width, gun_y,
                                               self.x + self.width + 8, gun_y + 5,
                                               fill="#34495e", outline="#1c2833")
            gun_tip = canvas.create_rectangle(self.x + self.width + 8, gun_y - 1,
                                              self.x + self.width + 11, gun_y + 6,
                                              fill="#f1c40f", outline="#d68910")
            hand = canvas.create_oval(self.x + self.width - 2, gun_y + 1,
                                      self.x + self.width + 3, gun_y + 6,
                                      fill="#f5cba7", outline="#d4ac0d")
            self.canvas_id = [body, head, eye1, eye2, mouth, collar, belt, buckle,
                              leg1, leg2, shoe1, shoe2, gun_body, gun_tip, hand]
        else:
            gun_body = canvas.create_rectangle(self.x - 8, gun_y,
                                               self.x, gun_y + 5,
                                               fill="#34495e", outline="#1c2833")
            gun_tip = canvas.create_rectangle(self.x - 11, gun_y - 1,
                                              self.x - 8, gun_y + 6,
                                              fill="#f1c40f", outline="#d68910")
            hand = canvas.create_oval(self.x - 3, gun_y + 1,
                                      self.x + 2, gun_y + 6,
                                      fill="#f5cba7", outline="#d4ac0d")
            self.canvas_id = [body, head, eye1, eye2, mouth, collar, belt, buckle,
                              leg1, leg2, shoe1, shoe2, gun_body, gun_tip, hand]
 
# ==========================================
# 模块 5: 敌人与生成器模块 (Enemy & Spawner)
# ==========================================
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.vx = 0
        self.vy = 0
        self.speed = 3
        self.hp = 5
        self.on_ground = False
        self.active = True 
        self.canvas_id = None
 
    def update(self, player_x, physics):
        self.vx = self.speed if player_x > self.x else -self.speed
        self.x += self.vx
        physics.apply_gravity_and_ground(self)
 
    def take_damage(self):
        self.hp -= 1
        if self.hp <= 0:
            self.active = False 
 
    def get_rect(self):
        return (self.x, self.y, self.width, self.height)
 
    def render(self, canvas):
        if self.canvas_id:
            for cid in self.canvas_id:
                canvas.delete(cid)
        if self.active:
            cx = self.x + self.width // 2 
            cy = self.y + self.height // 2
 
            shadow = canvas.create_oval(self.x + 2, self.y + self.height - 3,
                                        self.x + self.width - 2, self.y + self.height,
                                        fill="black", stipple="gray50", outline="")
 
            body = canvas.create_oval(self.x, self.y,
                                      self.x + self.width, self.y + self.height,
                                      fill="#e74c3c", outline="#922b21", width=3)
 
            inner = canvas.create_oval(self.x + 4, self.y + 4,
                                       self.x + self.width - 4, self.y + self.height - 4,
                                       fill="#ec7063", outline="")
 
            wiggle = int(2 * math.sin(self.x * 0.1))
            ant_l = canvas.create_line(cx - 6, self.y + 4,
                                       cx - 10 + wiggle, self.y - 6,
                                       fill="#922b21", width=2)
            ant_r = canvas.create_line(cx + 6, self.y + 4,
                                       cx + 10 - wiggle, self.y - 6,
                                       fill="#922b21", width=2)
            ant_l_tip = canvas.create_oval(cx - 11 + wiggle, self.y - 8,
                                           cx - 9 + wiggle, self.y - 6,
                                           fill="#f1c40f", outline="")
            ant_r_tip = canvas.create_oval(cx + 9 - wiggle, self.y - 8,
                                           cx + 11 - wiggle, self.y - 6,
                                           fill="#f1c40f", outline="")
 
            eye_y = self.y + 10
            eye1_w = canvas.create_oval(self.x + 6, eye_y, self.x + 13, eye_y + 8,
                                        fill="white", outline="#922b21", width=1)
            eye1_i = canvas.create_oval(self.x + 8, eye_y + 2, self.x + 11, eye_y + 6,
                                        fill="#f1c40f", outline="")
            eye1_p = canvas.create_oval(self.x + 9, eye_y + 3, self.x + 10, eye_y + 5,
                                        fill="black", outline="")
            eye2_w = canvas.create_oval(self.x + 17, eye_y, self.x + 24, eye_y + 8,
                                        fill="white", outline="#922b21", width=1)
            eye2_i = canvas.create_oval(self.x + 19, eye_y + 2, self.x + 22, eye_y + 6,
                                        fill="#f1c40f", outline="")
            eye2_p = canvas.create_oval(self.x + 20, eye_y + 3, self.x + 21, eye_y + 5,
                                        fill="black", outline="")
 
            tooth1 = canvas.create_polygon(self.x + 11, self.y + 22,
                                           self.x + 14, self.y + 22,
                                           self.x + 12, self.y + 26,
                                           fill="white", outline="#7b241c")
            tooth2 = canvas.create_polygon(self.x + 16, self.y + 22,
                                           self.x + 19, self.y + 22,
                                           self.x + 18, self.y + 26,
                                           fill="white", outline="#7b241c")
 
            claw_y = self.y + self.height - 2
            claws = []
            for offset in [4, 11, 18]:
                claws.append(canvas.create_polygon(
                    self.x + offset, claw_y,
                    self.x + offset + 2, claw_y + 4,
                    self.x + offset + 4, claw_y,
                    fill="#f1c40f", outline="#7b241c"
                ))
 
            bar_w = self.width
            bar_h = 3
            bar_x = self.x
            bar_y = self.y - 6
            bar_bg = canvas.create_rectangle(bar_x, bar_y, bar_x + bar_w, bar_y + bar_h,
                                             fill="#34495e", outline="")
            ratio = max(0, self.hp / 5)
            if ratio > 0:
                fill_color = "#2ecc71" if ratio > 0.5 else "#e74c3c"
                bar_fg = canvas.create_rectangle(bar_x, bar_y,
                                                 bar_x + int(bar_w * ratio), bar_y + bar_h,
                                                 fill=fill_color, outline="")
            else:
                bar_fg = None
 
            self.canvas_id = [shadow, body, inner, ant_l, ant_r, ant_l_tip, ant_r_tip,
                              eye1_w, eye1_i, eye1_p, eye2_w, eye2_i, eye2_p,
                              tooth1, tooth2, bar_bg] + claws 
            if bar_fg:
                self.canvas_id.append(bar_fg)
 
    def destroy(self, canvas):
        self.active = False
        if self.canvas_id is not None:
            if isinstance(self.canvas_id, list):
                for cid in self.canvas_id:
                    canvas.delete(cid)
            else:
                canvas.delete(self.canvas_id)
            self.canvas_id = None
 
class Spawner:
    def __init__(self, canvas_width, ground_y):
        self.canvas_width = canvas_width 
        self.ground_y = ground_y
        self.spawn_interval = 3.5 
        self.last_spawn_time = -1.0 
 
    def update(self, current_time, enemies_list):
        if current_time - self.last_spawn_time >= self.spawn_interval:
            self.last_spawn_time = current_time
            x = -30 if random.choice([True, False]) else self.canvas_width
            y = self.ground_y - 30
            enemies_list.append(Enemy(x, y))
 
# ==========================================
# 模块 1: 游戏引擎与主循环模块 (Game Engine)
# ==========================================
class GameEngine:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Python 2D 小游戏 (纯标准库)")
        self.width = 800
        self.height = 500
 
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="#87CEEB")
        self.canvas.pack()
        self.canvas.create_rectangle(0, Physics.GROUND_Y, self.width, self.height,
                                     fill="#228B22", outline="")
 
        # 状态：MENU / RUNNING / PAUSED / WIN / LOSE 
        self.state = "MENU"
        self.start_time = None
        self.paused_time = 0
        self.pause_start = 0
        self.kill_count = 0
 
        self.menu_btn_rect = (self.width // 2 - 110, self.height // 2 + 20,
                              self.width // 2 + 110, self.height // 2 + 80)
        self.restart_btn_rect = (self.width // 2 - 110, self.height // 2 + 60,
                                 self.width // 2 + 110, self.height // 2 + 120)
 
        self.input_manager = InputManager(self.root, self)
        self.player = Player(self.width // 2 - 15, Physics.GROUND_Y - 40)
        self.spawner = Spawner(self.width, Physics.GROUND_Y)
        self.enemies = []
        self.projectiles = []
 
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Button-1>", self.on_mouse_click)
 
        try:
            import ctypes
            ctypes.windll.imm32.ImmDisableIME(ctypes.windll.kernel32.GetCurrentThreadId())
        except Exception:
            pass
 
        self.loop()
 
    # ---------- 鼠标点击 ----------
    def on_mouse_click(self, event):
        x, y = event.x, event.y 
 
        if self.state == "MENU":
            x1, y1, x2, y2 = self.menu_btn_rect
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.start_game()
            return 
 
        if self.state in ["WIN", "LOSE"]:
            x1, y1, x2, y2 = self.restart_btn_rect
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.reset_game()
            return
 
    # ---------- 开始 / 重置 ----------
    def start_game(self):
        self.state = "RUNNING"
        self.start_time = time.time()
        self.paused_time = 0
        self.pause_start = 0 
        self.kill_count = 0
        self.player.hp = self.player.max_hp
        self.player.invincible_time = 0
        self.player.x = self.width // 2 - 15
        self.player.y = Physics.GROUND_Y - 40
        self.player.vx = self.player.vy = 0
        for e in self.enemies:
            e.destroy(self.canvas)
        for p in self.projectiles:
            p.destroy(self.canvas)
        self.enemies.clear()
        self.projectiles.clear()
        self.spawner.last_spawn_time = -1.0
        # 清理可能残留的菜单/结束画面元素
        self.canvas.delete("ui")
        self.canvas.delete("end")
        self.canvas.delete("menu")
 
    def reset_game(self):
        self.start_game()
 
    # ---------- 菜单渲染 ----------
    def render_menu(self):
        self.canvas.delete("ui")
        self.canvas.delete("end")
        self.canvas.delete("menu")
 
        # 深色星空背景
        for i in range(20):
            shade = int(20 + i * 4)
            blue = min(255, int(shade * 1.2))
            c = f"#{shade:02x}{shade:02x}{blue:02x}"
            self.canvas.create_rectangle(0, i * 25, self.width, (i + 1) * 25,
                                         fill=c, outline="", tags="menu")
 
        random.seed(42)
        for _ in range(60):
            sx = random.randint(0, self.width)
            sy = random.randint(0, self.height // 2)
            r = random.choice([1, 1, 2])
            self.canvas.create_oval(sx, sy, sx + r, sy + r,
                                    fill="#ecf0f1", outline="", tags="menu")
        random.seed()
 
        # 主标题（带阴影）
        self.canvas.create_text(self.width // 2 + 4, 120 + 4,
                                text="PYTHON 2D", fill="#1c1c2b",
                                font=("Arial", 56, "bold"), tags="menu")
        self.canvas.create_text(self.width // 2, 120,
                                text="PYTHON 2D", fill="#1abc9c",
                                font=("Arial", 56, "bold"), tags="menu")
 
        self.canvas.create_text(self.width // 2 + 3, 190 + 3,
                                text="SHOOTER", fill="#1c1c2b",
                                font=("Arial", 64, "bold"), tags="menu")
        self.canvas.create_text(self.width // 2, 190,
                                text="SHOOTER", fill="#f1c40f",
                                font=("Arial", 64, "bold"), tags="menu")
 
        self.canvas.create_text(self.width // 2, 260,
                                text="Survive 60 seconds  ·  Defeat all enemies",
                                fill="#bdc3c7", font=("Consolas", 14), tags="menu")
 
        x1, y1, x2, y2 = self.menu_btn_rect
        self.canvas.create_rectangle(x1 + 4, y1 + 4, x2 + 4, y2 + 4,
                                     fill="#1c1c2b", outline="", tags="menu")
        self.canvas.create_rectangle(x1, y1, x2, y2,
                                     fill="#16a085", outline="#1abc9c", width=3,
                                     tags="menu")
        self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                text="▶  START GAME", fill="white",
                                font=("Arial", 22, "bold"), tags="menu")
 
        self.canvas.create_text(self.width // 2, self.height - 60,
                                text="[A/D] Move   [K] Double Jump   [J] Shoot   [Space] Pause",
                                fill="#7f8c8d", font=("Consolas", 12), tags="menu")
        self.canvas.create_text(self.width // 2, self.height - 30,
                                text="v1.2  ·  Built with Python + Tkinter",
                                fill="#34495e", font=("Consolas", 10), tags="menu")
 
    # ---------- 暂停 ----------
    def toggle_pause(self):
        if self.state == "RUNNING":
            self.state = "PAUSED"
            self.pause_start = time.time()
        elif self.state == "PAUSED":
            self.state = "RUNNING"
            self.paused_time += time.time() - self.pause_start
 
    def get_elapsed_time(self):
        if self.state in ["WIN", "LOSE"]:
            if not hasattr(self, "_end_elapsed"):
                current = time.time()
                if self.state == "PAUSED":
                    self._end_elapsed = current - self.start_time - self.paused_time - (current - self.pause_start)
                else:
                    self._end_elapsed = current - self.start_time - self.paused_time
            return self._end_elapsed
 
        if hasattr(self, "_end_elapsed"):
            del self._end_elapsed
 
        current_time = time.time()
        if self.state == "PAUSED":
            return current_time - self.start_time - self.paused_time - (current_time - self.pause_start)
        return current_time - self.start_time - self.paused_time
 
    # ---------- 主循环 ----------
    def loop(self):
        # 菜单状态
        if self.state == "MENU":
            self.render_menu()
            self.root.after(16, self.loop)
            return
 
        # 游戏运行 
        if self.state == "RUNNING":
            self.update_entities()
            self.check_collisions()
            self.cleanup_entities()
            if self.player.hp <= 0:
                self.state = "LOSE"
 
        if self.state == "RUNNING" and self.get_elapsed_time() >= 60.0:
            self.state = "WIN"
 
        # 渲染场景 
        self.render_all()
 
        # 结束界面
        if self.state in ["WIN", "LOSE"]:
            self.render_end_screen()
            self.root.after(16, self.loop)
            return
 
        self.root.after(16, self.loop)
 
    def update_entities(self):
        elapsed = self.get_elapsed_time()
        self.player.update(self.input_manager, Physics, self.width)
        self.player.handle_jump(self.input_manager)
 
        if self.input_manager.is_pressed('j'):
            bullet = self.player.attack()
            if bullet:
                self.projectiles.append(bullet)
 
        self.spawner.update(elapsed, self.enemies)
        for enemy in self.enemies:
            enemy.update(self.player.x, Physics)
 
        for proj in self.projectiles:
            proj.update()
 
    def check_collisions(self):
        player_rect = self.player.get_rect()
 
        for proj in self.projectiles:
            if not proj.active:
                continue 
            proj_rect = proj.get_rect()
            for enemy in self.enemies:
                if not enemy.active:
                    continue
                if Collision.check_aabb(proj_rect, enemy.get_rect()):
                    enemy.take_damage()
                    proj.destroy(self.canvas)
                    if not enemy.active:
                        self.kill_count += 1
                    break
 
        for enemy in self.enemies:
            if not enemy.active:
                continue
            if Collision.check_aabb(player_rect, enemy.get_rect()):
                self.player.take_damage()
 
    def cleanup_entities(self):
        alive_enemies = []
        for e in self.enemies:
            if e.active:
                alive_enemies.append(e)
            else:
                e.destroy(self.canvas)
        self.enemies = alive_enemies
 
        alive_projectiles = []
        for p in self.projectiles:
            if p.active and 0 <= p.x <= self.width:
                alive_projectiles.append(p)
            else:
                p.destroy(self.canvas)
        self.projectiles = alive_projectiles
 
    def render_all(self):
        self.player.render(self.canvas)
        for enemy in self.enemies:
            enemy.render(self.canvas)
        for proj in self.projectiles:
            proj.render(self.canvas)
        self.render_ui()
 
   
    def render_ui(self):
        
        self.canvas.delete("ui")
        self.canvas.delete("end")
 
        # ---------- 1. 血量 ----------
        self.canvas.create_rectangle(8, 8, 140, 48,
                                     fill="#2c3e50", outline="#1abc9c", width=2,
                                     tags="ui")
        for i in range(self.player.max_hp):
            hx = 18 + i * 30
            hy = 16
            color = "#e74c3c" if i < self.player.hp else "#7f8c8d"
            outline = "#c0392b" if i < self.player.hp else "#34495e"
            self.canvas.create_polygon(
                hx, hy + 10, hx + 10, hy, hx + 20, hy + 10, hx + 10, hy + 25,
                fill=color, outline=outline, width=2, tags="ui"
            )
 
        # ---------- 2. 倒计时 ----------
        remaining = max(0, 60.0 - self.get_elapsed_time())
        if remaining > 30:
            tc = "#f1c40f"
        elif remaining > 10:
            tc = "#e67e22"
        else:
            tc = "#e74c3c"
        time_str = f"TIME  {remaining:04.1f}s"
 
        self.canvas.create_rectangle(self.width - 180, 10, self.width - 12, 180,
                                     fill="#2c3e50", outline="#1abc9c", width=2,
                                     tags="ui")
        self.canvas.create_text(self.width - 96, 35, text=time_str,
                                fill=tc, font=("Consolas", 18, "bold"),
                                tags="ui")
 
        # ---------- 3. 击杀数 ----------
        kill_str = f"KILLS  {self.kill_count}"
        self.canvas.create_text(self.width - 96, 75, text=kill_str,
                                fill="#f1c40f", font=("Consolas", 14, "bold"),
                                tags="ui")
 
        # ---------- 4. 操作提示 ----------
        hint = "[A/D] Move   [K] Jump x2   [J] Shoot   [Space] Pause"
        self.canvas.create_rectangle(8, self.height - 32,
                                     self.width - 8, self.height - 8,
                                     fill="#2c3e50", stipple="gray25",
                                     outline="#1abc9c", tags="ui")
        self.canvas.create_text(self.width // 2, self.height - 20,
                                text=hint, fill="#ecf0f1",
                                font=("Consolas", 12, "bold"), tags="ui")
 
        # ---------- 5. 暂停遮罩 ----------
        if self.state == "PAUSED":
            self.canvas.create_rectangle(0, 0, self.width, self.height,
                                         fill="black", stipple="gray50", tags="ui")
            self.canvas.create_text(self.width // 2, self.height // 2 - 20,
                                    text="PAUSED", fill="white",
                                    font=("Arial", 48, "bold"), tags="ui")
            self.canvas.create_text(self.width // 2, self.height // 2 + 30,
                                    text="Press SPACE to resume",
                                    fill="#bdc3c7", font=("Arial", 16), tags="ui")
 
    # ---------- 结束界面 ----------
    def render_end_screen(self):
        self.canvas.delete("end")
 
        self.canvas.create_rectangle(0, 0, self.width, self.height,
                                     fill="black", stipple="gray75", tags="end")
 
        msg = "YOU WIN!" if self.state == "WIN" else "GAME OVER"
        color = "#2ecc71" if self.state == "WIN" else "#e74c3c"
 
        self.canvas.create_text(self.width // 2, self.height // 2 - 80,
                                text=msg, fill=color,
                                font=("Arial", 64, "bold"), tags="end")
 
        stat = f"Kills: {self.kill_count}    Time: {self.get_elapsed_time():.1f}s"
        self.canvas.create_text(self.width // 2, self.height // 2,
                                text=stat, fill="#ecf0f1",
                                font=("Consolas", 18, "bold"), tags="end")
 
        x1, y1, x2, y2 = self.restart_btn_rect
        self.canvas.create_rectangle(x1 + 4, y1 + 4, x2 + 4, y2 + 4,
                                     fill="#1c1c2b", outline="", tags="end")
        self.canvas.create_rectangle(x1, y1, x2, y2,
                                     fill="#34495e", outline="#1abc9c", width=3,
                                     tags="end")
        self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                                text="RESTART", fill="#1abc9c",
                                font=("Arial", 22, "bold"), tags="end")
 
    def on_closing(self):
        self.root.destroy()
 
    def run(self):
        self.root.mainloop()
 
# ==========================================
# 启动入口
# ==========================================
if __name__ == "__main__":
    game = GameEngine()
    game.run()
