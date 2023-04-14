import pygame
import random
pygame.mixer.init()
pygame.font.init()

WIDTH, HEIGHT = 750, 750
GAME_WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Loading all the images
# Enemy ship's Images 
ENEMY_SHIP_RED = pygame.image.load("image-assets/enemy_ship_red.png")
ENEMY_SHIP_GRAY = pygame.image.load("image-assets/enemy_ship_gray.png")
ENEMY_SHIP_ORANGE = pygame.image.load("image-assets/enemy_ship_orange.png")

# Main Player's Ship
PLAYER_SHIP = pygame.image.load("image-assets/player_ship.png")

# Lasers
ENEMY_LASER_RED = pygame.image.load("image-assets/enemy_laser_red.png")
ENEMY_LASER_GRAY = pygame.image.load("image-assets/enemy_laser_blue.png")
ENEMY_LASER_ORANGE = pygame.image.load("image-assets/enemy_laser_orange.png")
PLAYER_LASER = pygame.image.load("image-assets/laser_main_player.png")

# Adding Background music
bg_sound = "sound-effects/bg_music.wav"

# Adding sound effects
laser_sound = pygame.mixer.Sound("sound-effects/laser.wav")
destruction_sound = pygame.mixer.Sound("sound-effects/explosion.wav")
get_hit_sound = pygame.mixer.Sound("sound-effects/get_hit_sound.wav")

# Background-images
BG = pygame.transform.scale(pygame.image.load("image-assets/background-black.png"), (WIDTH, HEIGHT))
starting_page = pygame.transform.scale(pygame.image.load("image-assets/start_page.png"), (WIDTH, HEIGHT))
lost_page = pygame.transform.scale(pygame.image.load("image-assets/lost_page.png"), (WIDTH, HEIGHT))
image1 = pygame.transform.scale(pygame.image.load("image-assets/player_ship.png"), (200, 200))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    def move(self, velocity):
        self.y += velocity
    
    def offscreen(self, height):
        return not(self.y <= height and self.y >= 0)
    
    def collision(self, obj):
        return collide(obj, self)

class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_image = None
        self.laser_image = None
        self.lasers = []
        self.cooldown_counter = 0
    
    def draw(self, window):
        window.blit(self.ship_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
    
    def move_lasers(self, velocity, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.offscreen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                get_hit_sound.play()
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x+57, self.y, self.laser_image)
            laser_sound.play()
            self.lasers.append(laser)
            self.cooldown_counter = 1

    def get_width(self):
        return self.ship_image.get_width()
    
    def get_height(self):
        return self.ship_image.get_height()
        
class Player(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.ship_image = PLAYER_SHIP
        self.laser_image = PLAYER_LASER
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.max_health = health
        self.score = 0

    def move_lasers(self, velocity, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.offscreen(HEIGHT):
                self.lasers.remove(laser)
            else: 
                for obj in objs:
                    if laser.collision(obj):
                        destruction_sound.play()
                        self.score += 2
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_image.get_height() - 20, self.ship_image.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_image.get_height() - 20, self.ship_image.get_width() * (self.health/self.max_health), 10))


class EnemyShip(Ship):
    COLOR_MAP = {
        "red": (ENEMY_SHIP_RED, ENEMY_LASER_RED),
        "blue": (ENEMY_SHIP_ORANGE, ENEMY_LASER_ORANGE),
        "green": (ENEMY_SHIP_GRAY, ENEMY_LASER_GRAY)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_image, self.laser_image = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_image)

    def move(self, velocity):
        self.y += velocity

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cooldown_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y))

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    timer = 300

    ingame_font = pygame.font.SysFont("Consolas", 25)
    end_font = pygame.font.SysFont("OCR A", 50)

    pygame.mixer.music.load(bg_sound)
    pygame.mixer.music.play(-1)
    
    enemies = []
    wave_length = 5
    enemy_velocity = 1

    player_velocity = 5
    laser_velocity = 5

    player = Player(300, 615)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
            GAME_WINDOW.blit(BG, (0, 0))

            # Showing text on the screen
            levels_score_label = ingame_font.render(f"Level: {level} || Score: {player.score}", 1, (0,255,0))
            lives_label = ingame_font.render(f"Lives(♥): {lives}", 1, (255,0,0))

            GAME_WINDOW.blit(levels_score_label, (10,10))
            GAME_WINDOW.blit(lives_label, (WIDTH - lives_label.get_width() - 10, 10))

            for enemy in enemies:
                enemy.draw(GAME_WINDOW)

            player.draw(GAME_WINDOW)

            if lost:
                GAME_WINDOW.blit(lost_page, (0,0))
                lost_label = end_font.render("You've lost!!!", 1, (255, 255, 255),)
                GAME_WINDOW.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 250))
                score_board_label = end_font.render(f"Your Final Score is {player.score}", 1, (255, 255, 255))
                GAME_WINDOW.blit(score_board_label, (WIDTH/2 - score_board_label.get_width()/2, 350))
                
                if timer == 480 or 420 or 360 or 300 or 240 or 180 or 120 or 60 or 0:
                    timer_label = end_font.render(f"The Game is restarting in  {round(timer/60)} s.", 1, (255, 255, 255))
                    GAME_WINDOW.blit(timer_label, (WIDTH/2 - timer_label.get_width()/2, 450))

            pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
            timer -= 1

        if lost:
            if lost_count > FPS * 5:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = EnemyShip(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_a] and player.x - player_velocity > 0 : # Left
            player.x -= player_velocity
        if keys[pygame.K_d] and player.x + player_velocity + player.get_width() < WIDTH: # Right
            player.x += player_velocity 
        if keys[pygame.K_w] and player.y - player_velocity > 0: # Up
            player.y -= player_velocity
        if keys[pygame.K_s] and player.y + player_velocity + player.get_height() - 5 < HEIGHT: # Down
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        
        player.move_lasers(-laser_velocity, enemies)

def main_menu():
    title_font = pygame.font.SysFont("Forte", 65)
    run = True
    while run:
        GAME_WINDOW.blit(starting_page, (0,0))
        title_label = title_font.render("Click to Start the Game!", 1, (255,255,255))
        GAME_WINDOW.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        GAME_WINDOW.blit(image1, (WIDTH/2 - PLAYER_SHIP.get_width()/2 - 20, 400))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()