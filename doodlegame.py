import pygame
import random

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doodle Jump")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (169, 169, 169)

player_width, player_height = 50, 50
player_x, player_y = WIDTH // 2 - player_width // 2, HEIGHT - player_height - 10
player_speed = 15
player_jump_speed = 15
gravity = 0.5
player_velocity = 0

platform_width, platform_height = 100, 10
platforms = []
platform_count = 5
corner_radius = 5
min_distance = 75
max_distance = 150
spring_height = 15
spring_recovery_speed = 10

font = pygame.font.SysFont(None, 55)

class Platform(pygame.Rect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_y = self.y
        self.sprung = False
        self.spring_offset = 0
        self.breakable = kwargs.get('breakable', False)
        self.broken = False
        self.parts = []
        self.part_speed = 0

    def update(self):
        if self.sprung:
            self.spring_offset += spring_recovery_speed
            if self.spring_offset >= spring_height:
                self.spring_offset = 0
                self.sprung = False
        else:
            self.spring_offset = 0

        if self.broken:
            self.part_speed += gravity
            for part in self.parts:
                part.y += self.part_speed

    def draw(self):
        if self.broken:
            for part in self.parts:
                pygame.draw.rect(screen, GRAY, part, border_radius=corner_radius)
        else:
            pygame.draw.rect(screen, BLACK, (self.x, self.y - self.spring_offset, self.width, self.height), border_radius=corner_radius)

    def break_platform(self):
        self.broken = True
        self.parts = [
            pygame.Rect(self.x, self.y, self.width // 2, self.height),
            pygame.Rect(self.x + self.width // 2, self.y, self.width // 2, self.height)
        ]

def create_initial_platforms():
    platforms.clear()
    x = WIDTH // 2 - platform_width // 2
    y = HEIGHT - platform_height
    start_platform = Platform(0, 600, 400, 10)
    platforms.append(start_platform)
    while len(platforms) < platform_count:
        x = random.randint(0, WIDTH - platform_width)
        y = random.randint(0, HEIGHT - platform_height)
        breakable = random.choice([True, False])
        new_platform = Platform(x, y, platform_width, platform_height, breakable=breakable)
        if not any(new_platform.colliderect(platform) for platform in platforms):
            platforms.append(new_platform)

def draw_platform(platform):
    platform.draw()

def display_message(message, color, position):
    text = font.render(message, True, color)
    rect = text.get_rect(center=position)
    screen.blit(text, rect)

def main():
    global player_x, player_y, player_velocity, platforms
    create_initial_platforms()
    
    running = True
    game_over = False
    while running:
        screen.fill(WHITE)
        
        if game_over:
            display_message("Ви програли!", RED, (WIDTH // 2, HEIGHT // 2 - 50))
            pygame.draw.rect(screen, BLUE, (WIDTH // 2 - 100, HEIGHT // 2 + 10, 200, 50))
            display_message("грати знову", WHITE, (WIDTH // 2, HEIGHT // 2 + 35))
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if WIDTH // 2 - 100 < x < WIDTH // 2 + 100 and HEIGHT // 2 + 10 < y < HEIGHT // 2 + 60:
                        player_x, player_y = WIDTH // 2 - player_width // 2, HEIGHT - player_height - 10
                        player_velocity = 0
                        create_initial_platforms()
                        game_over = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x - player_speed > 0:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] and player_x + player_speed < WIDTH - player_width:
                player_x += player_speed

            player_velocity += gravity
            player_y += player_velocity

            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            on_platform = False
            for platform in platforms:
                if player_rect.colliderect(platform) and player_velocity > 0:
                    player_velocity = -player_jump_speed
                    platform.sprung = True
                    on_platform = True
                    if platform.breakable and not platform.broken:
                        platform.break_platform()

            if player_y > HEIGHT:
                game_over = True

            if player_y < HEIGHT // 2:
                offset = HEIGHT // 2 - player_y
                player_y = HEIGHT // 2
                for platform in platforms:
                    platform.y += offset
                platforms = [p for p in platforms if p.y < HEIGHT]
                while len(platforms) < platform_count:
                    x = random.randint(0, WIDTH - platform_width)
                    y = min(p.y - platform_height for p in platforms) - random.randint(min_distance, max_distance)
                    breakable = random.choice([True, False])
                    new_platform = Platform(x, y, platform_width, platform_height, breakable=breakable)
                    if not any(new_platform.colliderect(platform) for platform in platforms):
                        platforms.append(new_platform)

            for platform in platforms:
                platform.update()
                draw_platform(platform)
            pygame.draw.rect(screen, BLUE, player_rect)

            pygame.display.flip()
            pygame.time.delay(30)

    pygame.quit()

main()
