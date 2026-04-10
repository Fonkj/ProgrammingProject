import pygame
import sys
import random

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

TOTAL_DISTANCE = 50 
PIXELS_PER_METER = 1080 

AUDIO_PATH = r"D:\Python\Project\Testing\Sound.wav" 
IMAGE_MARIO_PATH = r"D:\Python\Project\Testing\image14.png"
IMAGE_QUEEN_PATH = r"D:\Python\Project\Testing\image2.png"
IMAGE_BALL_PATH = r"D:\Python\Project\Testing\image3.png"
IMAGE_MONSTER_PATH = r"D:\Python\Project\Testing\image4.png"
IMAGE_LAKE_PATH = r"D:\Python\Project\Testing\image6.png"
IMAGE_CHASER_BALL_PATH = r"D:\Python\Project\Testing\image5.png"
IMAGE_CHASER_PATH = r"D:\Python\Project\Testing\image7.png"

SKY_BLUE = (100, 150, 255)
GROUND_BROWN = (139, 69, 19)
TEXT_WHITE = (255, 255, 255)
TEXT_YELLOW = (255, 220, 0)

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.theme_music = pygame.mixer.Sound(AUDIO_PATH)
            self.music_playing = False
        except pygame.error:
            print("Warning: Audio file not found. Playing silently.")
            self.theme_music = None
    def start_theme(self):
        if self.theme_music and not self.music_playing:
            self.theme_music.play(loops=-1)
            self.music_playing = True

class AssetLoader:
    def __init__(self):
        self.font_main = pygame.font.Font(None, 60)
        self.font_small = pygame.font.Font(None, 40)
        self.mario_image = self.load_bg(IMAGE_MARIO_PATH, 120, (255, 0, 0))
        self.queen_image = self.load_bg(IMAGE_QUEEN_PATH, 140, (255, 105, 180))
        self.ball_image = self.load_bg(IMAGE_BALL_PATH, 50, (255, 165, 0))
        self.monster_image = self.load_bg(IMAGE_MONSTER_PATH, 160, (128, 0, 128))
        self.chaser_ball_image = self.load_bg(IMAGE_CHASER_BALL_PATH, 50, (0, 255, 255))
        self.chaser_image = self.load_bg(IMAGE_CHASER_PATH, 140, (0, 100, 0))
        try:
            img = pygame.image.load(IMAGE_LAKE_PATH).convert_alpha()
            img.set_colorkey(img.get_at((0, 0)))
            self.lake_image = pygame.transform.scale(img, (450, 60))
        except pygame.error:
            self.lake_image = pygame.Surface((450, 60))
            self.lake_image.fill((0, 0, 255))
    def load_bg(self, path, target_height, fallback_color):
        try:
            img = pygame.image.load(path).convert_alpha()
            img.set_colorkey(img.get_at((0, 0)))
            w = int(img.get_width() * (target_height / img.get_height()))
            return pygame.transform.scale(img, (w, target_height))
        except pygame.error:
            fallback = pygame.Surface((target_height, target_height))
            fallback.fill(fallback_color)
            return fallback
        
class Mario(pygame.sprite.Sprite):
    def __init__(self, x, image):
        super().__init__()
        self.image_standing = image
        w, h = image.get_size()
        self.image_crouching = pygame.transform.scale(image, (w, h // 2))
        self.image = self.image_standing
        self.rect = self.image.get_rect(midbottom=(x, SCREEN_HEIGHT - 60))
        self.vy = 0
        self.gravity = 1.2
        self.jump_power = -13 
        self.base_speed = 15   
        self.sprint_speed = 25 
        self.crawl_speed = 15 
        self.on_ground = True
        self.is_crouching = False
        self.floor = SCREEN_HEIGHT - 60
    def update(self):
        keys = pygame.key.get_pressed()
        if self.is_crouching:
            active_speed = self.crawl_speed
        elif keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            active_speed = self.sprint_speed 
        else:
            active_speed = self.base_speed 
        scroll = 0 
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= active_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.rect.centerx > SCREEN_WIDTH // 2:
                scroll = active_speed
            else:
                self.rect.x += active_speed
        if self.rect.left < 0: self.rect.left = 0
        self.vy += self.gravity
        self.rect.y += self.vy
        if self.rect.bottom >= self.floor:
            self.rect.bottom = self.floor
            self.on_ground = True
            self.vy = 0
        if self.is_crouching and self.on_ground:
            self.image = self.image_crouching
            self.rect = self.image.get_rect(midbottom=(self.rect.centerx, self.floor))
        else:
            self.image = self.image_standing
            self.rect = self.image.get_rect(midbottom=(self.rect.centerx, self.rect.bottom))
        self.rect.inflate_ip(-15, -15)
        return scroll 
    def jump(self):
        if self.on_ground and not self.is_crouching:
            self.vy = self.jump_power
            self.on_ground = False
    def crouch(self, state):
        self.is_crouching = state

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, is_high_obstacle):
        super().__init__()
        if is_high_obstacle:
            self.image = pygame.Surface((60, 40)); self.image.fill((50, 50, 50))
            y_pos = SCREEN_HEIGHT - 130 
        else:
            self.image = pygame.Surface((50, 60)); self.image.fill((150, 50, 50))
            y_pos = SCREEN_HEIGHT - 60
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH + 100, y_pos))
    def update(self, scroll):
        self.rect.x -= scroll
        if self.rect.right < 0: self.kill()

class Lake(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(SCREEN_WIDTH + 100, SCREEN_HEIGHT - 60))
        self.rect.inflate_ip(-40, -20) 
    def update(self, scroll):
        self.rect.x -= scroll
        if self.rect.right < 0: self.kill()

class PowerBall(pygame.sprite.Sprite):
    def __init__(self, x, y, image): 
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))       
        self.vx = random.randint(-18, 5) 
        self.vy = random.randint(-14, -2)         
        self.gravity = 0.6
        self.floor = SCREEN_HEIGHT - 60
    def update(self, scroll):
        self.rect.x += self.vx - scroll
        self.vy += self.gravity
        self.rect.y += self.vy       
        if self.rect.bottom >= self.floor:
            self.rect.bottom = self.floor
            self.vy = -16 
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH: 
            self.kill()


class FlyingMonster(pygame.sprite.Sprite):
    def __init__(self, image, ball_image):
        super().__init__()
        self.image = image; self.ball_image = ball_image
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH + 200, 250))
        self.target_x = SCREEN_WIDTH - 200
        self.state = "ENTERING"
        self.balls_thrown = 0
        self.throw_timer = 0
    def update(self, powerball_group, mario):
        if self.state == "ENTERING":
            self.rect.x -= 8 
            if self.rect.centerx <= self.target_x:
                self.state = "THROWING"
                self.throw_timer = pygame.time.get_ticks()              
        elif self.state == "THROWING":
            
            if self.rect.centerx < mario.rect.centerx:
                self.rect.x += 3
            elif self.rect.centerx > mario.rect.centerx:
                self.rect.x -= 3
            if self.balls_thrown < 8:
                if pygame.time.get_ticks() - self.throw_timer > 600:
                    powerball_group.add(PowerBall(self.rect.centerx, self.rect.bottom, self.ball_image))
                    self.balls_thrown += 1
                    self.throw_timer = pygame.time.get_ticks()
            else:
                self.state = "LEAVING"               
        elif self.state == "LEAVING":
            self.rect.y -= 8; self.rect.x += 5 
            if self.rect.bottom < 0: self.kill()

class ChaserBall(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.original_image = image 
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = random.randint(15, 27)  
        self.vy = random.randint(-35, -8) 
        self.gravity = 0.8
        self.floor = SCREEN_HEIGHT - 60
        self.angle = 0 
    def update(self, scroll):
        self.rect.x += self.vx - scroll
        self.vy += self.gravity
        self.rect.y += self.vy
        self.angle = (self.angle - 15) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.inflate_ip(-10, -10) 
        if self.rect.bottom >= self.floor:
            self.rect.bottom = self.floor
            self.vy = -12 
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0: 
            self.kill()

class PowerBall(pygame.sprite.Sprite):
    def __init__(self, x, y, image, target_x):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))       
        dist_x = target_x - x
        self.vx = (dist_x / 30) + random.randint(-6, 6)    
        if self.vx > 22: self.vx = 22
        if self.vx < -22: self.vx = -22       
        self.vy = random.randint(-15, -5)
        self.gravity = 0.6
        self.floor = SCREEN_HEIGHT - 60
    def update(self, scroll):
        self.rect.x += self.vx - scroll
        self.vy += self.gravity
        self.rect.y += self.vy       
        if self.rect.bottom >= self.floor:
            self.rect.bottom = self.floor
            self.vy = -16 
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH: 
            self.kill()


class FlyingMonster(pygame.sprite.Sprite):
    def __init__(self, image, ball_image):
        super().__init__()
        self.image = image; self.ball_image = ball_image
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH + 200, 250))
        self.target_x = SCREEN_WIDTH - 200
        self.state = "ENTERING"
        self.balls_thrown = 0
        self.throw_timer = 0
    def update(self, powerball_group, mario):
        if self.state == "ENTERING":
            self.rect.x -= 8 
            if self.rect.centerx <= self.target_x:
                self.state = "THROWING"
                self.throw_timer = pygame.time.get_ticks()               
        elif self.state == "THROWING":
            if self.rect.centerx < mario.rect.centerx:
                self.rect.x += 5
            elif self.rect.centerx > mario.rect.centerx:
                self.rect.x -= 5
            if self.balls_thrown < 8:
                if pygame.time.get_ticks() - self.throw_timer > 600:                    
                    keys = pygame.key.get_pressed()
                    predicted_offset = 0                                    
                    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                        current_speed = 25 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 15
                        predicted_offset = current_speed * 15                                         
                    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                        current_speed = 25 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 15
                        predicted_offset = -(current_speed * 15)                   
                    predicted_x = mario.rect.centerx + predicted_offset                   
                    powerball_group.add(PowerBall(self.rect.centerx, self.rect.bottom, self.ball_image, predicted_x))                    
                    self.balls_thrown += 1
                    self.throw_timer = pygame.time.get_ticks()
            else:
                self.state = "LEAVING"               
        elif self.state == "LEAVING":
            self.rect.y -= 8; self.rect.x += 5 
            if self.rect.bottom < 0: self.kill()

class ChasingMonster(pygame.sprite.Sprite):
    def __init__(self, image, ball_image):
        super().__init__()
        self.image = image; self.ball_image = ball_image
        self.rect = self.image.get_rect(midbottom=(-200, SCREEN_HEIGHT - 60))
        self.target_x = 100 
        self.state = "ENTERING"
        self.throw_timer = 0
    def update(self, chaserball_group, meters):
        if meters >= 49: 
            self.state = "LEAVING"
        if self.state == "ENTERING":
            self.rect.x += 6 
            if self.rect.centerx >= self.target_x:
                self.state = "THROWING"
                self.throw_timer = pygame.time.get_ticks()
        elif self.state == "THROWING":
            if pygame.time.get_ticks() - self.throw_timer > 1300: 
                chaserball_group.add(ChaserBall(self.rect.right, self.rect.centery, self.ball_image))
                self.throw_timer = pygame.time.get_ticks()
        elif self.state == "LEAVING":
            self.rect.x -= 8 
            if self.rect.right < 0: self.kill()

class Queen(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH + 200, SCREEN_HEIGHT - 60))
    def update(self, scroll):
        self.rect.x -= scroll

class MarioRunnerGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mario Epic Rescue Dash - The Chaos Update!")
        self.clock = pygame.time.Clock()
        self.sounds = SoundManager()
        self.assets = AssetLoader()
        self.state = "READY"
        self.mario = Mario(200, self.assets.mario_image) 
        self.queen = pygame.sprite.GroupSingle()
        self.obstacles = pygame.sprite.Group() 
        self.flying_boss = pygame.sprite.GroupSingle()
        self.powerballs = pygame.sprite.Group()
        self.chasing_boss = pygame.sprite.GroupSingle()
        self.chaser_balls = pygame.sprite.Group()
        self.pixels_walked = 0 
        self.obstacle_spawn_counter = 0
        self.ground_scroll = 0
        self.boss1_spawned = False
        self.lake_spawned = False
        self.boss2_spawned = False
    def reset_game(self):
        self.mario = Mario(200, self.assets.mario_image)
        self.obstacles.empty(); self.queen.empty()
        self.flying_boss.empty(); self.powerballs.empty()
        self.chasing_boss.empty(); self.chaser_balls.empty()
        self.boss1_spawned = False
        self.lake_spawned = False
        self.boss2_spawned = False
        self.pixels_walked = 0
        self.obstacle_spawn_counter = 0
        self.state = "PLAYING"
        self.sounds.start_theme()
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_UP]:
                    if self.state in ["READY", "WIN", "LOSE"]: self.reset_game()
                    elif self.state == "PLAYING": self.mario.jump()
                if event.key == pygame.K_DOWN and self.state == "PLAYING":
                    self.mario.crouch(True)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN and self.state == "PLAYING":
                    self.mario.crouch(False)
    def update(self):
        if self.state == "PLAYING":
            scroll = self.mario.update()
            self.pixels_walked += scroll
            self.ground_scroll = (self.ground_scroll - scroll) % 100
            meters = self.pixels_walked / PIXELS_PER_METER
            self.obstacles.update(scroll)
            self.queen.update(scroll)
            self.powerballs.update(scroll)
            self.chaser_balls.update(scroll)
            self.flying_boss.update(self.powerballs, self.mario)
            self.chasing_boss.update(self.chaser_balls, meters)
            if meters >= 25 and not self.boss1_spawned:
                self.flying_boss.add(FlyingMonster(self.assets.monster_image, self.assets.ball_image))
                self.boss1_spawned = True
            if meters >= 30 and not self.lake_spawned:
                self.obstacles.add(Lake(self.assets.lake_image))
                self.lake_spawned = True
            if meters >= 40 and not self.boss2_spawned:
                self.chasing_boss.add(ChasingMonster(self.assets.chaser_image, self.assets.chaser_ball_image))
                self.boss2_spawned = True
            boss1_active = self.flying_boss.sprite and self.flying_boss.sprite.state != "LEAVING"
            boss2_active = self.chasing_boss.sprite and self.chasing_boss.sprite.state != "LEAVING"
            if scroll > 0 and not (boss1_active or boss2_active):
                self.obstacle_spawn_counter += scroll
                if self.obstacle_spawn_counter > random.randint(600, 1000): 
                    if not (29 < meters < 33): 
                        self.obstacles.add(Obstacle(random.choice([True, False])))
                    self.obstacle_spawn_counter = 0
            elif meters >= TOTAL_DISTANCE and not self.queen.sprite:
                self.queen.add(Queen(self.assets.queen_image))
            if (pygame.sprite.spritecollide(self.mario, self.obstacles, False) or 
                pygame.sprite.spritecollide(self.mario, self.powerballs, False) or
                pygame.sprite.spritecollide(self.mario, self.chaser_balls, False)):
                self.state = "LOSE"
            if self.queen.sprite and pygame.sprite.collide_rect(self.mario, self.queen.sprite):
                self.state = "WIN"

    def draw(self):
        self.screen.fill(SKY_BLUE)
        ground_y = SCREEN_HEIGHT - 60
        pygame.draw.rect(self.screen, GROUND_BROWN, (0, ground_y, SCREEN_WIDTH, 60))
        for x in range(-100, SCREEN_WIDTH + 100, 100):
            pygame.draw.rect(self.screen, (100, 50, 10), (x + self.ground_scroll, ground_y, 10, 60))
        if self.state != "READY":
            self.obstacles.draw(self.screen)
            self.screen.blit(self.mario.image, self.mario.rect)
            self.powerballs.draw(self.screen)
            self.chaser_balls.draw(self.screen) 
            self.flying_boss.draw(self.screen)
            self.chasing_boss.draw(self.screen) 
            self.queen.draw(self.screen)
        if self.state == "READY":
            txt = self.assets.font_main.render("PRESS SPACE TO START DASH", True, TEXT_WHITE)
            self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        elif self.state == "PLAYING":
            meters = self.pixels_walked / PIXELS_PER_METER
            dist_left = max(0, TOTAL_DISTANCE - meters)
            dist_txt = self.assets.font_small.render(f"Distance to Queen: {int(dist_left)}m", True, TEXT_YELLOW)
            self.screen.blit(dist_txt, (20, 20))
            boss1_active = self.flying_boss.sprite and self.flying_boss.sprite.state != "LEAVING"
            boss2_active = self.chasing_boss.sprite and self.chasing_boss.sprite.state != "LEAVING"
            if boss1_active or boss2_active:
                warn_txt = self.assets.font_main.render("WARNING: BOSS INCOMING!", True, (255, 0, 0))
                self.screen.blit(warn_txt, (SCREEN_WIDTH//2 - 250, 50))
        elif self.state == "LOSE":
            bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); bg.set_alpha(150); bg.fill((0, 0, 0))
            self.screen.blit(bg, (0, 0))
            txt = self.assets.font_main.render("Hahaha you lose Mario, beat me next time huh!?", True, (255, 50, 50))
            self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
            sub = self.assets.font_small.render("Press Space to Restart", True, TEXT_WHITE)
            self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60)))
        elif self.state == "WIN":
            bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); bg.set_alpha(150); bg.fill((255, 255, 255))
            self.screen.blit(bg, (0, 0))
            txt = self.assets.font_main.render("Congratulations, you save the Queen!", True, (0, 150, 0))
            self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
            sub = self.assets.font_small.render("Press Space to Play Again", True, (0, 0, 0))
            self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60)))
        pygame.display.flip()
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
if __name__ == "__main__":
    game = MarioRunnerGame()
    game.run()