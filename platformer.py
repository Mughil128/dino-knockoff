import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer Game - Trial Thing")

clock = pygame.time.Clock()
FPS = 60

SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (50, 205, 50)
DIRT_BROWN = (139, 69, 19)
PLAYER_COLOR = (30, 144, 255)
OBSTACLE_COLOR = (220, 20, 60)
TEXT_COLOR = (30, 30, 30)

font = pygame.font.SysFont("consolas", 36, bold=True)

player = pygame.Rect(100, HEIGHT - 140, 50, 60)
player_vel_y = 0
gravity = 0.9
jump_power = 18
on_ground = False

ground_height = 80
ground = pygame.Rect(0, HEIGHT - ground_height, WIDTH, ground_height)

obstacles = []
obstacle_width = 40
obstacle_height = 60
obstacle_speed = 5
spawn_timer = 0
spawn_interval = 1600  

game_over = False
score = 0
high_scores = []
start_ticks = pygame.time.get_ticks()

def reset_game():
    global player, player_vel_y, on_ground, obstacles, game_over
    global spawn_timer, score, start_ticks, obstacle_speed, spawn_interval
    player.x, player.y = 100, HEIGHT - 140
    player_vel_y = 0
    on_ground = False
    obstacles.clear()
    game_over = False
    spawn_timer = 0
    score = 0
    obstacle_speed = 5
    spawn_interval = 1600
    start_ticks = pygame.time.get_ticks()

def draw_text_center(text, y, size=36, color=TEXT_COLOR):
    font_local = pygame.font.SysFont("Segoe UI", size, bold=True)
    msg = font_local.render(text, True, color)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, y))

def update_difficulty(seconds):
    global obstacle_speed, spawn_interval
    obstacle_speed = 5 + seconds * 0.1 
    spawn_interval = max(600, 1600 - seconds * 20)

def update_high_scores(new_score):
    high_scores.append(new_score)
    high_scores.sort(reverse=True)
    if len(high_scores) > 5:
        high_scores.pop()

running = True
while running:
    dt = clock.tick(FPS)
    screen.fill(SKY_BLUE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            reset_game()

    if not game_over:
        seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
        score = seconds_passed
        update_difficulty(score)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and on_ground:
            player_vel_y = -jump_power
            on_ground = False

        player_vel_y += gravity
        player.y += player_vel_y

        if player.colliderect(ground):
            player.bottom = ground.top
            player_vel_y = 0
            on_ground = True
        else:
            on_ground = False

        for obs in obstacles:
            obs.x -= obstacle_speed
        obstacles = [obs for obs in obstacles if obs.right > 0]

        spawn_timer += dt
        if spawn_timer > spawn_interval:
            spawn_timer = 0
            x = WIDTH + random.randint(0, 250)
            y = ground.top - obstacle_height
            obstacles.append(pygame.Rect(x, y, obstacle_width, obstacle_height))

        for obs in obstacles:
            if player.colliderect(obs):
                update_high_scores(score)
                game_over = True
                break

        pygame.draw.rect(screen, DIRT_BROWN, ground)
        pygame.draw.rect(screen, GRASS_GREEN, (0, HEIGHT - ground_height, WIDTH, 20))
        pygame.draw.rect(screen, PLAYER_COLOR, player, border_radius=8)
        for obs in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, obs, border_radius=6)

        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (10, 10))

    else:
        draw_text_center("Game Over!", HEIGHT // 2 - 70, 48, OBSTACLE_COLOR)
        draw_text_center("Press R to Restart", HEIGHT // 2 - 20, 30)

        draw_text_center("Top 5 Scores", HEIGHT // 2 + 30, 32)
        for i, s in enumerate(high_scores):
            draw_text_center(f"{i + 1} - {s}", HEIGHT // 2 + 70 + i * 30, 28)

    pygame.display.flip()
