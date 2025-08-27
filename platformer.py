import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("platformer game - improved trial")

clock = pygame.time.Clock()
fps = 60

jump_sound = pygame.mixer.Sound("jump.wav")
game_over_sound = pygame.mixer.Sound("game_over.wav")

pygame.mixer.music.load("bg_music.wav")
pygame.mixer.music.set_volume(0.7)  
pygame.mixer.music.play(-1)     

sky_blue = (135, 206, 235)
grass_green = (53, 120, 71)
dirt_brown = (139, 69, 19)
obstacle_color = (200, 40, 60)
text_color = (30, 30, 30)
white = (255, 255, 255)

sprite_sheet = pygame.image.load("JumpingCats.png").convert_alpha()
sprite_width = sprite_sheet.get_width() // 13
sprite_height = sprite_sheet.get_height() // 5

player_frames = []
for i in range(13):
    frame = sprite_sheet.subsurface(pygame.Rect(i * sprite_width, 0, sprite_width, sprite_height))
    frame = pygame.transform.scale(frame, (50, 60))
    player_frames.append(frame)

player_frame_index = 0
player_anim_timer = 0
player_anim_speed = 50

font = pygame.font.SysFont("consolas", 36, bold=True)

player = pygame.Rect(100, height - 140, 50, 60)
player_vel_y = 0
gravity = 0.9
jump_power = 18
on_ground = False

ground_height = 80
ground = pygame.Rect(0, height - ground_height, width, ground_height)

clouds = [[random.randint(0, width), random.randint(50, 200)] for _ in range(5)]
hills = [[x, height - ground_height - 50] for x in range(0, width, 200)]

obstacles = []
obstacle_speed = 5
spawn_timer = 0
spawn_interval = 1600  

particles = []

game_over = False
score = 0
high_scores = []
start_ticks = pygame.time.get_ticks()
state = "start"

save_file = "highscores.txt"
if os.path.exists(save_file):
    with open(save_file, "r") as f:
        high_scores = [int(line.strip()) for line in f.readlines()]

def save_high_scores():
    with open(save_file, "w") as f:
        for s in high_scores:
            f.write(str(s) + "\n")

def reset_game():
    global player, player_vel_y, on_ground, obstacles, game_over
    global spawn_timer, score, start_ticks, obstacle_speed, spawn_interval, state
    player.x, player.y = 100, height - 140
    player_vel_y = 0
    on_ground = False
    obstacles.clear()
    game_over = False
    spawn_timer = 0
    score = 0
    obstacle_speed = 5
    spawn_interval = 1600
    start_ticks = pygame.time.get_ticks()
    state = "running"

def draw_text_center(text, y, size=36, color=text_color):
    font_local = pygame.font.SysFont("Segoe UI", size, bold=True)
    msg = font_local.render(text, True, color)
    screen.blit(msg, (width // 2 - msg.get_width() // 2, y))

def update_difficulty(seconds):
    global obstacle_speed, spawn_interval
    obstacle_speed = min(12, 5 + seconds * 0.1) 
    spawn_interval = max(500, 1600 - seconds * 20)

def update_high_scores(new_score):
    high_scores.append(new_score)
    high_scores.sort(reverse=True)
    if len(high_scores) > 5:
        high_scores.pop()
    save_high_scores()

def spawn_particle(x, y):
    particles.append([x, y, random.randint(-2, 2), -random.randint(1, 3), random.randint(4, 7)])

def draw_particles():
    for p in particles[:]:
        x, y, vx, vy, life = p
        pygame.draw.circle(screen, white, (int(x), int(y)), max(1, life // 2))
        p[0] += vx
        p[1] += vy
        p[4] -= 1
        if p[4] <= 0:
            particles.remove(p)

def draw_background():
    for hill in hills:
        hill[0] -= 1
        if hill[0] < -300:
            hill[0] = width + random.randint(0, 200)
            hill[1] = height - ground_height - random.randint(40, 90)
        pygame.draw.ellipse(screen, (25, 120, 25), (hill[0], hill[1], 350, 160))
        pygame.draw.ellipse(screen, (34, 177, 76), (hill[0] + 20, hill[1] + 10, 310, 140))

    for cloud in clouds:
        cloud[0] -= 2
        if cloud[0] < -150:
            cloud[0] = width + random.randint(0, 200)
            cloud[1] = random.randint(50, 200)
        pygame.draw.ellipse(screen, white, (cloud[0], cloud[1], 120, 70))
        pygame.draw.ellipse(screen, white, (cloud[0] + 50, cloud[1] - 30, 90, 70))
        pygame.draw.ellipse(screen, white, (cloud[0] + 80, cloud[1] + 10, 110, 70))
        pygame.draw.ellipse(screen, white, (cloud[0] + 20, cloud[1] - 20, 100, 60))
        pygame.draw.ellipse(screen, white, (cloud[0] + 60, cloud[1] + 25, 90, 55))

def spawn_obstacle():
    height_choice = random.choice([40, 60, 80])
    width_choice = random.choice([40, 50, 60])
    x = width + random.randint(0, 200)
    y = ground.top - height_choice
    return pygame.Rect(x, y, width_choice, height_choice)

running = True
while running:
    dt = clock.tick(fps)
    screen.fill(sky_blue)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_high_scores()
            pygame.quit()
            sys.exit()
        if state == "start" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            reset_game()
        if state == "game_over" and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            reset_game()

    if state == "start":
        draw_text_center("Welcome to Platformer!", height // 2 - 60, 48, text_color)
        draw_text_center("Press Space to Start", height // 2, 32, obstacle_color)
        pygame.display.flip()
        continue

    if state == "running":
        seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
        score = seconds_passed
        update_difficulty(score)

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and on_ground:
            player_vel_y = -jump_power
            on_ground = False
            jump_sound.play()
            for _ in range(8):
                spawn_particle(player.centerx, player.bottom)

        player_vel_y += gravity
        player.y += player_vel_y

        if player.colliderect(ground):
            if not on_ground:
                for _ in range(6):
                    spawn_particle(player.centerx, ground.top)
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
            obstacles.append(spawn_obstacle())

        for obs in obstacles:
            deadly_zone = pygame.Rect(obs.left, obs.top, obs.width, obs.height // 2)  
            if player.colliderect(deadly_zone):
                update_high_scores(score)
                game_over_sound.play()
                game_over = True
                state = "game_over"
                break

        draw_background()
        pygame.draw.rect(screen, dirt_brown, ground)
        pygame.draw.rect(screen, grass_green, (0, height - ground_height, width, 20))

        player_anim_timer += dt
        if player_anim_timer >= player_anim_speed:
            player_anim_timer = 0
            player_frame_index = (player_frame_index + 1) % len(player_frames)

        screen.blit(player_frames[player_frame_index], player.topleft)

        for obs in obstacles:
            spike_count = obs.width // 20
            spike_width = obs.width / spike_count
            for i in range(spike_count):
                x1 = obs.left + i * spike_width
                x2 = x1 + spike_width / 2
                x3 = x1 + spike_width
                y_top = obs.top
                y_base = obs.bottom
                pygame.draw.polygon(screen, obstacle_color, [(x1, y_base), (x2, y_top), (x3, y_base)])

        draw_particles()

        score_text = font.render(f"Score: {score}", True, text_color)
        screen.blit(score_text, (10, 10))

    elif state == "game_over":
        lines = []
        lines.append(("Game Over!", 48, obstacle_color))
        lines.append(("Press R to Restart", 30, text_color))
        lines.append(("Top 5 Scores", 32, text_color))
        for i, s in enumerate(high_scores):
            lines.append((f"{i + 1}. {s} points", 28, text_color))

        total_height = sum(pygame.font.SysFont("Segoe UI", size, bold=True).size(text)[1] + 15
                        for text, size, _ in lines)

        start_y = height // 2 - total_height // 2

        y = start_y
        for text, size, color in lines:
            draw_text_center(text, y, size, color)
            y += pygame.font.SysFont("Segoe UI", size, bold=True).size(text)[1] + 15

    pygame.display.flip()