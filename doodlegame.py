import pygame
import random
import tkinter as tk
from tkinter import ttk

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
gravity = 0.4
player_velocity = 20

platform_width, platform_height = 100, 10
platforms = []
platform_count = 4
corner_radius = 5
min_distance = 90
max_distance = 140
spring_height = 15
spring_recovery_speed = 10
RECORD = 0
with open('record.txt', 'r', encoding='UTF8') as file:
    hey = file.read()
    if hey:
        RECORD = int(hey)
    else:
        RECORD = 0


font = pygame.font.SysFont(None, 55)

# Load player images
player_images = [
    pygame.transform.scale(pygame.image.load("i/player1.png"), (player_width, player_height)),
    pygame.transform.scale(pygame.image.load("i/player2.png"), (player_width, player_height))
]
selected_player_image = None

def create_platform(x, y, width=platform_width, height=platform_height, breakable=False):
    return {
        'rect': pygame.Rect(x, y, width, height),
        'original_y': y,
        'sprung': False,
        'spring_offset': 0,
        'breakable': breakable,
        'broken': False,
        'parts': [],
        'part_speed': 0
    }

def update_platform(platform):
    if platform['sprung']:
        platform['spring_offset'] += spring_recovery_speed
        if platform['spring_offset'] >= spring_height:
            platform['spring_offset'] = 0
            platform['sprung'] = False
    else:
        platform['spring_offset'] = 0

    if platform['broken']:
        platform['part_speed'] += gravity
        for part in platform['parts']:
            part.y += platform['part_speed']

def draw_platform(platform):
    if platform['broken']:
        for part in platform['parts']:
            pygame.draw.rect(screen, GRAY, part, border_radius=corner_radius)
    else:
        pygame.draw.rect(screen, BLACK, (platform['rect'].x, platform['rect'].y - platform['spring_offset'], platform['rect'].width, platform['rect'].height), border_radius=corner_radius)

def break_platform(platform):
    platform['broken'] = True
    platform['parts'] = [
        pygame.Rect(platform['rect'].x, platform['rect'].y, platform['rect'].width // 2, platform['rect'].height),
        pygame.Rect(platform['rect'].x + platform['rect'].width // 2, platform['rect'].y, platform['rect'].width // 2, platform['rect'].height)
    ]

def create_initial_platforms():
    global platforms
    platforms.clear()
    start_platform = create_platform(0, HEIGHT - platform_height, width=WIDTH)
    platforms.append(start_platform)
    while len(platforms) < platform_count//2:
        x = random.randint(0, WIDTH - platform_width)
        y = random.randint(100, 200)
        breakable = random.choice([True, False])
        new_platform = create_platform(x, y, breakable=breakable)
        if not any(new_platform['rect'].colliderect(p['rect']) for p in platforms):
            platforms.append(new_platform)
    while len(platforms) < platform_count:
        x = random.randint(0, WIDTH - platform_width)
        y = random.randint(300, 400)
        breakable = random.choice([True, False])
        new_platform = create_platform(x, y, breakable=breakable)
        if not any(new_platform['rect'].colliderect(p['rect']) for p in platforms):
            platforms.append(new_platform)

def display_message(message, color, position):
    text = font.render(message, True, color)
    rect = text.get_rect(center=position)
    screen.blit(text, rect)

def character_selection_screen():
    global selected_player_image
    running = True
    while running:
        screen.fill(WHITE)
        display_message("Виберіть персонажа", BLACK, (WIDTH // 2, HEIGHT // 2 - 100))
        
        button1_rect = pygame.Rect(WIDTH // 4 - 50, HEIGHT // 2 - 50, 100, 100)
        button2_rect = pygame.Rect(3 * WIDTH // 4 - 50, HEIGHT // 2 - 50, 100, 100)
        
        screen.blit(player_images[0], button1_rect.topleft)
        screen.blit(player_images[1], button2_rect.topleft)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if button1_rect.collidepoint(x, y):
                    selected_player_image = player_images[0]
                    running = False
                elif button2_rect.collidepoint(x, y):
                    selected_player_image = player_images[1]
                    running = False
    return True

def main():
    global player_x, player_y, player_velocity, platforms, RECORD
    if not character_selection_screen():
        return
    
    create_initial_platforms()
    score = 0
    visited = []
    running = True
    game_over = False
    while running:
        screen.fill(RED)
        pygame.font.init() # you have to call this at the start, 
        # if you want to use this module.
        my_font = pygame.font.SysFont('Comic Sans MS', 30)
        text_surface = my_font.render(str(score), False, (0, 0, 0))
        line = 'Record: ' + str(RECORD)
        text_record = my_font.render(line, False, (0, 0, 0))

        screen.blit(text_surface, (0,0))
        screen.blit(text_record, (0,30))

        if game_over:
            if RECORD<score:
                with open("record.txt", 'w', encoding='UTF8') as file:
                    file.write(str(score))
                RECORD = score
            score = 0
            display_message("Ви програли!", RED, (WIDTH // 2, HEIGHT // 2 - 50))
            pygame.draw.rect(screen, BLUE, (WIDTH // 2 - 150, HEIGHT // 2 + 10, 300, 50))
            display_message("Грати знову", WHITE, (WIDTH // 2, HEIGHT // 2 + 35))
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
                if player_rect.colliderect(platform['rect']) and player_velocity > 0:
                    player_velocity = -player_jump_speed
                    platform['sprung'] = True
                    on_platform = True
                    if platform not in visited:
                        score+=1
                        visited.append(platform)
                    print(score)
                    if platform['breakable'] and not platform['broken']:
                        break_platform(platform)

            if player_y > HEIGHT:
                game_over = True

            if player_y < HEIGHT // 2:
                offset = HEIGHT // 2 - player_y
                player_y = HEIGHT // 2
                for platform in platforms:
                    platform['rect'].y += offset
                platforms = [p for p in platforms if p['rect'].y < HEIGHT]
                while len(platforms) < platform_count:
                    x = random.randint(0, WIDTH - platform_width)
                    y = min(p['rect'].y - platform_height for p in platforms) - random.randint(min_distance, max_distance)
                    breakable = random.choice([True, False])
                    new_platform = create_platform(x, y, breakable=breakable)
                    if not any(new_platform['rect'].colliderect(p['rect']) for p in platforms):
                        platforms.append(new_platform)

            for platform in platforms:
                update_platform(platform)
                draw_platform(platform)
            
            screen.blit(selected_player_image, (player_x, player_y))

            pygame.display.flip()
            pygame.time.delay(30)

    pygame.quit()


main()
