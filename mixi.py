import pygame
import sys
import random

# --- Configuration & Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Timers
TIME_CALLING = 10
TIME_CHASE = 20
TIME_TOTAL = TIME_CALLING + TIME_CHASE + 10 # 40s total

# Paths
AUDIO_PATH = r"D:\Python\New chap\Ấn Độ Mixi (Nà Ná Na Na Anh Độ Mixi).wav"
HOUSE_PATH = r"D:\Python\New chap\image4.png"

# --- OOP: Asset and Component Managers ---

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

class SpriteManager:
    def __init__(self):
        self.mixi_frames = self.load_character_animations("mixi", "image1.png")
        self.vu_frames = self.load_character_animations("vu", "image2.png")
        
        # Load Flip-flop
        try:
            ff_img = pygame.image.load("image3.png").convert_alpha()
            self.flipflop_image = pygame.transform.scale(ff_img, (50, 50))
        except pygame.error:
            self.flipflop_image = pygame.Surface((30, 15), pygame.SRCALPHA)
            pygame.draw.ellipse(self.flipflop_image, (0, 200, 200), (0, 0, 30, 15))
            
        # Load Safe House Achievement
        try:
            house_raw = pygame.image.load(HOUSE_PATH).convert_alpha()
            scale_h = 432 # 60% of screen height
            w = int(house_raw.get_width() * (scale_h / house_raw.get_height()))
            self.house_image = pygame.transform.scale(house_raw, (w, scale_h))
        except pygame.error:
            self.house_image = pygame.Surface((400, 432))
            self.house_image.fill((100, 100, 255))

    def load_character_animations(self, name, image_filename):
        try:
            full_img = pygame.image.load(image_filename).convert_alpha()
            scale_height = 160 
            full_img = pygame.transform.scale(full_img, (int(full_img.get_width() * (scale_height / full_img.get_height())), scale_height))
            frame1 = full_img
            frame2 = pygame.transform.flip(full_img, True, False) 
            return [frame1, frame2]
        except pygame.error:
            color = (255, 0, 0) if name == "mixi" else (0, 255, 0)
            f1 = pygame.Surface((100, 160)); f1.fill(color)
            f2 = pygame.Surface((100, 160)); f2.fill((color[0], color[1], 100))
            return [f1, f2]

# --- OOP: Encapsulated Sprites ---

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, frames):
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.anim_timer = pygame.time.get_ticks()

    def animate(self):
        if pygame.time.get_ticks() - self.anim_timer > 150: 
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.anim_timer = pygame.time.get_ticks()

class Vu(Entity):
    def __init__(self, x, y, frames):
        super().__init__(x, y, frames)
        self.speed = 12
        self.floor = SCREEN_HEIGHT - 60 

    def update(self):
        self.rect.bottom = self.floor
        keys = pygame.key.get_pressed()
        moving = False
        
        # Player Controls!
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            moving = True
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            moving = True
            
        if moving:
            self.animate()
        else:
            self.image = self.frames[0] # Stand still if not pressing keys

class DoMixi(Entity):
    def __init__(self, x, y, frames, projectiles_group, flipflop_img):
        super().__init__(x, y, frames)
        self.speed = 7 # Mixi is slower than Vu
        self.projectiles_group = projectiles_group
        self.flipflop_image = flipflop_img
        self.throw_timer = pygame.time.get_ticks()
        self.floor = SCREEN_HEIGHT - 60
        self.throws_completed = 0

    def update(self):
        self.rect.x += self.speed # Auto-run independently
        self.rect.bottom = self.floor
        self.animate()
        self.throw_flipflop()

    def throw_flipflop(self):
        if self.throws_completed < 5:
            if pygame.time.get_ticks() - self.throw_timer > 3500:
                ff = FlipFlop(self.rect.centerx, self.rect.top, self.flipflop_image, self.throws_completed)
                self.projectiles_group.add(ff)
                self.throw_timer = pygame.time.get_ticks()
                self.throws_completed += 1

class FlipFlop(pygame.sprite.Sprite):
    def __init__(self, x, y, image, throw_index):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=(x, y))
        trajectories = [(18, -25), (22, -20), (15, -30), (25, -15), (19, -28)]
        self.vx = trajectories[throw_index][0]
        self.vy = trajectories[throw_index][1]
        self.gravity = 0.8

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vy += self.gravity
        if self.rect.top > SCREEN_HEIGHT - 60:
            self.kill()

class WinEnding(pygame.sprite.Sprite):
    def __init__(self, x, img):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect(midbottom=(x, SCREEN_HEIGHT - 60))

# --- OOP: Modular Game Controller ---

class MixiGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mixigaming: Alo Vu a Vu - Epic Chase")
        self.clock = pygame.time.Clock()
        self.font_dialog = pygame.font.Font(None, 40)
        self.font_main = pygame.font.Font(None, 50)
        
        self.sound_mgr = SoundManager()
        self.sprites = SpriteManager()
        
        self.state = "CALLING"
        self.start_ticks = pygame.time.get_ticks()
        
        self.all_sprites = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.achievement_group = pygame.sprite.GroupSingle()
        
        self.vu = Vu(600, SCREEN_HEIGHT - 60, self.sprites.vu_frames)
        self.all_sprites.add(self.vu)
        self.domixi = None
        self.camera_x = 0

    def update_states(self):
        elapsed = (pygame.time.get_ticks() - self.start_ticks) / 1000

        if self.state == "CALLING":
            if elapsed > 5 and self.domixi is None:
                self.domixi = DoMixi(self.vu.rect.x - 350, SCREEN_HEIGHT - 60, self.sprites.mixi_frames, self.projectiles, self.sprites.flipflop_image)
                self.all_sprites.add(self.domixi)
            if elapsed > TIME_CALLING:
                self.state = "CHASING"
                self.sound_mgr.start_theme()

        elif self.state == "CHASING":
            self.vu.update()
            self.projectiles.update()
            self.domixi.update()
            self.camera_x = self.vu.rect.centerx - (SCREEN_WIDTH // 2)

            # Spawn house exactly at 30 seconds
            if elapsed > TIME_CALLING + TIME_CHASE and not self.achievement_group.sprite:
                safe_house = WinEnding(self.vu.rect.x + 800, self.sprites.house_image)
                self.achievement_group.add(safe_house)

            # --- Collision Logic ---
            # 1. Did Mixi or a shoe touch Vu? -> CAUGHT!
            if pygame.sprite.collide_rect(self.vu, self.domixi) or pygame.sprite.spritecollide(self.vu, self.projectiles, False):
                self.state = "CAUGHT"
                self.vu.image = self.vu.frames[0] # Freeze animation
                self.domixi.image = self.domixi.frames[0]

            # 2. House logic
            if self.achievement_group.sprite:
                house = self.achievement_group.sprite
                
                # Stop Mixi if he hits the house wall
                if self.domixi.rect.right > house.rect.left:
                    self.domixi.rect.right = house.rect.left
                
                # Instant Win if Vu touches the house!
                if pygame.sprite.collide_rect(self.vu, house):
                    self.state = "ENDING_WIN"
                    self.vu.rect.left = house.rect.left + 50 # Pull him inside visually
                    self.vu.image = self.vu.frames[0] # Freeze animation
                    self.domixi.image = self.domixi.frames[0]

            if elapsed > TIME_TOTAL:
                self.state = "ENDING_TIMEOUT"

        elif self.state in ["CAUGHT", "ENDING_WIN", "ENDING_TIMEOUT"]:
            # EVERYTHING IS FROZEN EXCEPT THE MUSIC AND TIMER
            if elapsed > TIME_TOTAL:
                pygame.quit()
                sys.exit()

    def draw(self):
        self.screen.fill((135, 206, 235))
        ground_y = SCREEN_HEIGHT - 60
        pygame.draw.rect(self.screen, (50, 150, 50), (0, ground_y, SCREEN_WIDTH, 60))
        
        # Parallax background
        grass_offset = self.camera_x % 100
        for x in range(-100, SCREEN_WIDTH + 100, 100):
            pygame.draw.rect(self.screen, (40, 120, 40), (x - grass_offset, ground_y, 50, 60)) 
        cloud_offset = (self.camera_x // 3) % 400
        for x in range(-400, SCREEN_WIDTH + 400, 400):
            pygame.draw.ellipse(self.screen, (255, 255, 255), (x - cloud_offset + 100, 100, 160, 60)) 
            pygame.draw.ellipse(self.screen, (255, 255, 255), (x - cloud_offset + 280, 160, 100, 40)) 

        elapsed = (pygame.time.get_ticks() - self.start_ticks) / 1000

        # Draw the House first so characters are in front of it
        if self.achievement_group.sprite:
            house = self.achievement_group.sprite
            self.screen.blit(house.image, (house.rect.x - self.camera_x, house.rect.y))

        if self.state == "CALLING":
            self.screen.blit(self.vu.frames[0], (self.vu.rect.x - self.camera_x, self.vu.rect.y))
            if elapsed > 5 and self.domixi:
                self.screen.blit(self.domixi.frames[0], (self.domixi.rect.x - self.camera_x, self.domixi.rect.y))
                dialog_rect = pygame.Rect(self.domixi.rect.x - self.camera_x - 50, self.domixi.rect.y - 80, 200, 60)
                pygame.draw.rect(self.screen, (255, 255, 255), dialog_rect, border_radius=10)
                pygame.draw.rect(self.screen, (0, 0, 0), dialog_rect, 3, border_radius=10)
                txt = self.font_dialog.render("Alo Vũ à Vũ", True, (0, 0, 0))
                self.screen.blit(txt, txt.get_rect(center=dialog_rect.center))

        else:
            # Draw Sprites and Projectiles
            for sprite in self.all_sprites:
                self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))
            for proj in self.projectiles:
                self.screen.blit(proj.image, (proj.rect.x - self.camera_x, proj.rect.y))

        # --- DRAW POP-UP MENUS ---
        if self.state == "ENDING_WIN":
            victory_rect = pygame.Rect(SCREEN_WIDTH//2 - 400, SCREEN_HEIGHT//2 - 100, 800, 100)
            pygame.draw.rect(self.screen, (100, 255, 100), victory_rect, border_radius=15)
            pygame.draw.rect(self.screen, (0, 150, 0), victory_rect, 5, border_radius=15)
            txt = self.font_main.render("VICTORY! SAFE HOUSE SECURED.", True, (0, 0, 0))
            self.screen.blit(txt, txt.get_rect(center=victory_rect.center))

        elif self.state == "CAUGHT":
            popup_rect = pygame.Rect(SCREEN_WIDTH//2 - 450, SCREEN_HEIGHT//2 - 100, 900, 100)
            pygame.draw.rect(self.screen, (255, 200, 0), popup_rect, border_radius=15)
            pygame.draw.rect(self.screen, (255, 0, 0), popup_rect, 5, border_radius=15)
            txt = self.font_dialog.render("You've been caught, now you have to eat Mixi's fried chicken!!!", True, (0, 0, 0))
            self.screen.blit(txt, txt.get_rect(center=popup_rect.center))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.update_states()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = MixiGame()
    game.run()