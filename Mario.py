import pygame
import sys
import random

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_SPEED = 15 
TIME_TO_WIN = 20 

AUDIO_PATH = r"D:\Python\Project\Testing\Sound.wav"
IMAGE_MARIO_PATH = r"D:\Python\Project\Testing\image14.png"
IMAGE_QUEEN_PATH = r"D:\Python\Project\Testing\image2.png"

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
            print(f"Warning: Audio file not found at {AUDIO_PATH}. Playing silently.")
            self.theme_music = None
    def start_theme(self):
        if self.theme_music and not self.music_playing:
            self.theme_music.play(loops=-1)
            self.music_playing = True

class AssetLoader:
    def __init__(self):
        self.font_main = pygame.font.Font(None, 60)
        self.font_small = pygame.font.Font(None, 40)
        self.mario_image = self.load_and_remove_bg(IMAGE_MARIO_PATH, 120)
        self.queen_image = self.load_and_remove_bg(IMAGE_QUEEN_PATH, 140)
    def load_and_remove_bg(self, path, target_height):
        """Loads image, scales it, and automatically removes the background color."""
        try:
            img = pygame.image.load(path).convert_alpha()
            bg_color = img.get_at((0, 0)) 
            img.set_colorkey(bg_color)
            w = int(img.get_width() * (target_height / img.get_height()))
            return pygame.transform.scale(img, (w, target_height))
        except pygame.error:
            print(f"Warning: Could not load {path}. Using fallback rectangles.")
            fallback = pygame.Surface((80, target_height))
            fallback.fill((255, 0, 0) if "1" in path else (255, 105, 180))
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
        self.gravity = 1.5
        self.jump_power = -22
        self.on_ground = True
        self.is_crouching = False
        self.floor = SCREEN_HEIGHT - 60
    def update(self):
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
    def jump(self):
        if self.on_ground and not self.is_crouching:
            self.vy = self.jump_power
            self.on_ground = False
    def crouch(self, state):
        self.is_crouching = state

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, is_high_obstacle):
        super().__init__()
        self.is_high = is_high_obstacle
        if self.is_high:
            self.image = pygame.Surface((60, 40))
            self.image.fill((50, 50, 50)) 
            y_pos = SCREEN_HEIGHT - 130 
        else:
            self.image = pygame.Surface((50, 60))
            self.image.fill((150, 50, 50)) 
            y_pos = SCREEN_HEIGHT - 60
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH + 100, y_pos))
    def update(self):
        self.rect.x -= GAME_SPEED
        if self.rect.right < 0:
            self.kill()

class Queen(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH + 200, SCREEN_HEIGHT - 60))
    def update(self):
        self.rect.x -= GAME_SPEED

class MarioRunnerGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mario Epic Rescue Dash")
        self.clock = pygame.time.Clock()
        self.sounds = SoundManager()
        self.assets = AssetLoader()
        self.state = "READY" 
        self.start_ticks = 0
        self.mario = Mario(200, self.assets.mario_image) 
        self.queen = pygame.sprite.GroupSingle()
        self.obstacles = pygame.sprite.Group()
        self.obstacle_timer = 0
        self.ground_scroll = 0
    def reset_game(self):
        self.mario = Mario(200, self.assets.mario_image)
        self.obstacles.empty()
        self.queen.empty()
        self.state = "PLAYING"
        self.start_ticks = pygame.time.get_ticks()
        self.sounds.start_theme()
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if self.state == "READY" or self.state in ["WIN", "LOSE"]:
                        self.reset_game()
                    elif self.state == "PLAYING":
                        self.mario.jump()
                if event.key == pygame.K_DOWN and self.state == "PLAYING":
                    self.mario.crouch(True)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN and self.state == "PLAYING":
                    self.mario.crouch(False)
    def update(self):
        if self.state == "PLAYING":
            self.mario.update()
            self.obstacles.update()
            self.queen.update()
            self.ground_scroll = (self.ground_scroll - GAME_SPEED) % 100
            elapsed_seconds = (pygame.time.get_ticks() - self.start_ticks) / 1000
            if elapsed_seconds < TIME_TO_WIN:
                if pygame.time.get_ticks() - self.obstacle_timer > random.randint(800, 1500): 
                    is_high = random.choice([True, False])
                    self.obstacles.add(Obstacle(is_high))
                    self.obstacle_timer = pygame.time.get_ticks()
            elif not self.queen.sprite:
                self.queen.add(Queen(self.assets.queen_image))
            if pygame.sprite.spritecollide(self.mario, self.obstacles, False):
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
            self.screen.blit(self.mario.image, self.mario.rect)
            self.obstacles.draw(self.screen)
            self.queen.draw(self.screen)
        if self.state == "READY":
            txt = self.assets.font_main.render("PRESS SPACE TO START DASH", True, TEXT_WHITE)
            self.screen.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        elif self.state == "PLAYING":
            elapsed = (pygame.time.get_ticks() - self.start_ticks) / 1000
            dist_left = max(0, TIME_TO_WIN - elapsed)
            dist_txt = self.assets.font_small.render(f"Distance to Queen: {int(dist_left)}m", True, TEXT_YELLOW)
            self.screen.blit(dist_txt, (20, 20))
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