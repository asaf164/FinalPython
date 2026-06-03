"""
Author: Asaf Biran
program name - FinalProjectClient
Description: Multiplayer Pygame client for a two player car dodging game.
             connects to server, renders gameplay, and syncs state with FinalProjectProtocol.

"""



import pygame
import sys
import random
import socket
import threading
import logging
import FinalProjectProtocol


# logging setup
logging.basicConfig(
    filename='game_client.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)




SERVER_IP = "127.0.0.1"
PORT = 5555

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    logging.info("Attempting connection to server...")
    client_socket.connect((SERVER_IP, PORT))

    player_id = client_socket.recv(1024).decode('utf-8').strip()
    print(f"Connected successfully! You are Player: {player_id}")
    logging.info(f"Successfully connected as Player: {player_id}")
except Exception as e:
    print(f"Failed to connect to server: {e}")
    logging.error(f"Failed to connect to server: {e}")
    sys.exit()




pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(f"Car Game - Player {player_id}")


WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
PINK = (255, 105, 180)

LANES_P1 = [100, 200, 300]
LANES_P2 = [500, 600, 700]

CAR_WIDTH = 40
CAR_HEIGHT = 70
PLAYER_Y = 500

player1_lane = 1
player2_lane = 1
player1_alive = True
player2_alive = True
player1_lives = 3
player2_lives = 3
game_over = False
game_started = False


OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_SPEED = 5
obstacles_p1 = []
obstacles_p2 = []
hearts_p1 = []
hearts_p2 = []



"""
Times and fonts:
Configures timed events (such as obstacle spawning)
and loads fonts for on screen text.
"""
SPAWN_OBSTACLE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_OBSTACLE_EVENT, 1200)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)
win_font = pygame.font.SysFont("Arial", 60, bold=True)


"""
Server listener:
Background thread that continuously receives and processes messages from the server.
"""
def receive_data():
    global player1_lane, player2_lane, player1_alive, player2_alive, player1_lives, player2_lives, game_started
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                logging.warning("Received empty data. Server connection dropped.")
                break

            messages = data.split('\n')
            for msg in messages:
                parsed = FinalProjectProtocol.parse_msg(msg)
                if not parsed:
                    continue

                if parsed[0] == "START":
                    game_started = True
                    logging.info("Game start signal processed")
                elif parsed[0] == "SPAWN_OBS":
                    lane = parsed[1]
                    logging.info(f"Opponent spawned an obstacle in lane {lane}.")
                    if player_id == "1":
                        obstacles_p2.append([lane, -OBSTACLE_HEIGHT])
                    else:
                        obstacles_p1.append([lane, -OBSTACLE_HEIGHT])
                elif parsed[0] == "SPAWN_HEART":
                    lane = parsed[1]
                    logging.info(f"Opponent spawned a heart in lane {lane}.")
                    if player_id == "1":
                        hearts_p2.append([lane, -OBSTACLE_HEIGHT])
                    else:
                        hearts_p1.append([lane, -OBSTACLE_HEIGHT])
                elif parsed[0] == "UPDATE":
                    opp_lane, opp_alive, opp_lives = parsed[1], parsed[2], parsed[3]

                    if player_id == "1":
                        player2_lane = opp_lane
                        player2_alive = opp_alive
                        player2_lives = opp_lives
                    else:
                        player1_lane = opp_lane
                        player1_alive = opp_alive
                        player1_lives = opp_lives
        except:
            logging.error("Exception occurred inside the background thread loop.")
            break

logging.info("Launching background data receiver thread")
threading.Thread(target=receive_data, daemon=True).start()



"""
Main loop:
handles events, sends updates, updates game logic, and renders all visuals.
"""
while True:
    screen.fill(WHITE)

    if not game_started:
        text_waiting = font.render("Waiting for Player 2...", True, BLACK)
        screen.blit(text_waiting, (SCREEN_WIDTH // 2 - text_waiting.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.time.delay(100)
        continue

    if not player1_alive or not player2_alive:
        game_over = True

    try:
        if player_id == "1":
            client_socket.send(FinalProjectProtocol.build_update(player1_lane, player1_alive, player1_lives))
        else:
            client_socket.send(FinalProjectProtocol.build_update(player2_lane, player2_alive, player2_lives))
    except:
        print("Connection to the server lost.")
        logging.error("Connection to the server lost.")
        break


    """
    Event handlers:
    keyboard input, player quitting and obstacle/heart spawning.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            logging.info("Application closed by user.")
            pygame.quit()
            sys.exit()

        if event.type == SPAWN_OBSTACLE_EVENT and not game_over:
            lane = random.randint(0, 2)
            if player_id == "1" and player1_alive:
                if random.random() < 0.20:
                    hearts_p1.append([lane, -OBSTACLE_HEIGHT])
                    client_socket.send(FinalProjectProtocol.build_spawn_heart(lane))
                    logging.info(f"P1 spawned a heart in lane {lane}.")

                else:
                    obstacles_p1.append([lane, -OBSTACLE_HEIGHT])
                    client_socket.send(FinalProjectProtocol.build_spawn_obs(lane))
                    logging.info(f"P1 spawned an obstacle in lane {lane}.")

            if player_id == "2" and player2_alive:
                if random.random() < 0.20:
                    hearts_p2.append([lane, -OBSTACLE_HEIGHT])
                    client_socket.send(FinalProjectProtocol.build_spawn_heart(lane))
                    logging.info(f"P2 spawned a heart in lane {lane}.")
                else:
                    obstacles_p2.append([lane, -OBSTACLE_HEIGHT])
                    client_socket.send(FinalProjectProtocol.build_spawn_obs(lane))
                    logging.info(f"P2 spawned an obstacle in lane {lane}.")

        if event.type == pygame.KEYDOWN and not game_over:
            if player_id == "1" and player1_alive:
                if event.key == pygame.K_a and player1_lane > 0:
                    player1_lane -= 1
                    logging.info(f"Player 1 moved left to lane {player1_lane}.")
                if event.key == pygame.K_d and player1_lane < 2:
                    player1_lane += 1
                    logging.info(f"Player 1 moved right to lane {player1_lane}.")
            if player_id == "2" and player2_alive:
                if event.key == pygame.K_a and player2_lane > 0:
                    player2_lane -= 1
                    logging.info(f"Player 2 moved left to lane {player2_lane}.")
                if event.key == pygame.K_d and player2_lane < 2:
                    player2_lane += 1
                    logging.info(f"Player 2 moved right to lane {player2_lane}.")




    """
    Movement and collision handling:
    Moves obstacles and hearts downward, detect collisions, and updates player lives accordingly.
    """
    if not game_over:
        for obs in obstacles_p1[:]:
            obs[1] += OBSTACLE_SPEED
            if obs[1] > SCREEN_HEIGHT: obstacles_p1.remove(obs)
        for heart in hearts_p1[:]:
            heart[1] += OBSTACLE_SPEED
            if heart[1] > SCREEN_HEIGHT: hearts_p1.remove(heart)

        for obs in obstacles_p2[:]:
            obs[1] += OBSTACLE_SPEED
            if obs[1] > SCREEN_HEIGHT: obstacles_p2.remove(obs)
        for heart in hearts_p2[:]:
            heart[1] += OBSTACLE_SPEED
            if heart[1] > SCREEN_HEIGHT: hearts_p2.remove(heart)

        if player1_alive:
            p1_x = LANES_P1[player1_lane] - (CAR_WIDTH // 2)
            rect_p1 = pygame.Rect(p1_x, PLAYER_Y, CAR_WIDTH, CAR_HEIGHT)

            for obs in obstacles_p1[:]:
                obs_x = LANES_P1[obs[0]] - (OBSTACLE_WIDTH // 2)
                if rect_p1.colliderect(pygame.Rect(obs_x, obs[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT)):
                    obstacles_p1.remove(obs)
                    if player_id == "1":
                        player1_lives -= 1
                        logging.info(f"Player 1 hit an obstacle. Remaining lives: {player1_lives}")
                        if player1_lives <= 0:
                            player1_alive = False
                            logging.warning("Player 1 eliminated.")

            for heart in hearts_p1[:]:
                heart_x = LANES_P1[heart[0]] - (OBSTACLE_WIDTH // 2)
                if rect_p1.colliderect(pygame.Rect(heart_x, heart[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT)):
                    hearts_p1.remove(heart)
                    if player_id == "1":
                        player1_lives += 1
                        logging.info(f"Player 1 hit a heart. Total lives: {player1_lives}")

        if player2_alive:
            p2_x = LANES_P2[player2_lane] - (CAR_WIDTH // 2)
            rect_p2 = pygame.Rect(p2_x, PLAYER_Y, CAR_WIDTH, CAR_HEIGHT)

            for obs in obstacles_p2[:]:
                obs_x = LANES_P2[obs[0]] - (OBSTACLE_WIDTH // 2)
                if rect_p2.colliderect(pygame.Rect(obs_x, obs[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT)):
                    obstacles_p2.remove(obs)
                    if player_id == "2":
                        player2_lives -= 1
                        logging.info(f"Player 2 hit an obstacle. Remaining lives: {player2_lives}")
                        if player2_lives <= 0:
                            player2_alive = False
                            logging.warning("Player 2 eliminated.")

            for heart in hearts_p2[:]:
                heart_x = LANES_P2[heart[0]] - (OBSTACLE_WIDTH // 2)
                if rect_p2.colliderect(pygame.Rect(heart_x, heart[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT)):
                    hearts_p2.remove(heart)
                    if player_id == "2":
                        player2_lives += 1
                        logging.info(f"Player 2 hit a heart. Total lives: {player2_lives}")


    #drawing section

    pygame.draw.rect(screen, GRAY, (50, 0, 300, SCREEN_HEIGHT))
    pygame.draw.rect(screen, GRAY, (450, 0, 300, SCREEN_HEIGHT))

    for lane_x in LANES_P1[1:]: pygame.draw.line(screen, YELLOW, (lane_x - 50, 0), (lane_x - 50, SCREEN_HEIGHT), 5)
    for lane_x in LANES_P2[1:]: pygame.draw.line(screen, YELLOW, (lane_x - 50, 0), (lane_x - 50, SCREEN_HEIGHT), 5)

    for obs in obstacles_p1:
        obs_x = LANES_P1[obs[0]] - (OBSTACLE_WIDTH // 2)
        pygame.draw.rect(screen, ORANGE, (obs_x, obs[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

    for obs in obstacles_p2:
        obs_x = LANES_P2[obs[0]] - (OBSTACLE_WIDTH // 2)
        pygame.draw.rect(screen, ORANGE, (obs_x, obs[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

    for heart in hearts_p1:
        heart_x = LANES_P1[heart[0]] - (OBSTACLE_WIDTH // 2)
        pygame.draw.rect(screen, PINK, (heart_x, heart[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

    for heart in hearts_p2:
        heart_x = LANES_P2[heart[0]] - (OBSTACLE_WIDTH // 2)
        pygame.draw.rect(screen, PINK, (heart_x, heart[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

    if player1_alive:
        p1_x = LANES_P1[player1_lane] - (CAR_WIDTH // 2)
        pygame.draw.rect(screen, RED, (p1_x, PLAYER_Y, CAR_WIDTH, CAR_HEIGHT))

    if player2_alive:
        p2_x = LANES_P2[player2_lane] - (CAR_WIDTH // 2)
        pygame.draw.rect(screen, BLUE, (p2_x, PLAYER_Y, CAR_WIDTH, CAR_HEIGHT))

    lives_text_p1 = font.render(f"P1 Lives: {player1_lives}", True, RED)
    lives_text_p2 = font.render(f"P2 Lives: {player2_lives}", True, BLUE)
    screen.blit(lives_text_p1, (60, 10))
    screen.blit(lives_text_p2, (460, 10))


    """
    Game over screen: 
    Display the winner or tie result once a player loses all lives.
    """
    if game_over:
        if not player1_alive and player2_alive:
            win_text = "PLAYER 2 WINS!"
            text_color = BLUE
        elif not player2_alive and player1_alive:
            win_text = "PLAYER 1 WINS!"
            text_color = RED
        else:
            win_text = "IT'S A TIE!"
            text_color = BLACK

        text_game_over = win_font.render(win_text, True, text_color)

        bg_rect = text_game_over.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        pygame.draw.rect(screen, WHITE, bg_rect.inflate(20, 20))
        pygame.draw.rect(screen, BLACK, bg_rect.inflate(20, 20), 3)

        screen.blit(text_game_over, bg_rect)

    pygame.display.flip()
    clock.tick(60)