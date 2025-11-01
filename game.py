import os
import sys
import time
import random
import pygame
import voice
from voice import speak

# --- Configuration ---
WIDTH, HEIGHT = 600, 400
FPS = 60
ROUND_LIMIT = 10
import os
import sys
import time
import random
import pygame
from voice import speak

# --- Configuration ---
WIDTH, HEIGHT = 600, 400
FPS = 60
ROUND_LIMIT = 10
SCORE_FILE = "score.txt"
VOICE_ENABLED = True
AUTO_PLAY = os.environ.get('AUTO_PLAY') == '1'

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHT_GREEN = (0, 200, 0)


def speak_async(text: str):
    print('[main] speak_async called with:', repr(text))
    speak(text, VOICE_ENABLED)


# --- Game logic helpers ---
def get_winner(player, computer):
    if player == computer:
        return "It's a Tie!"
    elif (player == "Snake" and computer == "Water") or \
         (player == "Water" and computer == "Gun") or \
         (player == "Gun" and computer == "Snake"):
        return "You Win!"
    else:
        return "Computer Wins!"


def load_scores():
    p = 0
    c = 0
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("player:"):
                        p = int(line.split(":", 1)[1])
                    elif line.startswith("computer:"):
                        c = int(line.split(":", 1)[1])
        except Exception:
            p, c = 0, 0
    return p, c


def save_scores(p, c):
    try:
        with open(SCORE_FILE, "w") as f:
            f.write(f"player:{p}\n")
            f.write(f"computer:{c}\n")
    except Exception:
        pass


def _choose_font(size, bold=False):
    candidates = [
        "Montserrat", "Segoe UI", "Impact", "Arial Black", "Calibri", "Verdana",
        "Arial", "Tahoma"
    ]
    for name in candidates:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f and f.size("A"):
                return f
        except Exception:
            continue
    return pygame.font.Font(None, size)


def _create_vertical_gradient(w, h, top_color, bottom_color):
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
    return surf


def draw_background(surface):
    try:
        bg_image = pygame.transform.scale(pygame.image.load("background.jpg"), (WIDTH, HEIGHT))
        surface.blit(bg_image, (0, 0))
    except Exception:
        top = (16, 32, 64)
        bottom = (80, 160, 200)
        gradient = _create_vertical_gradient(WIDTH, HEIGHT, top, bottom)
        surface.blit(gradient, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 8):
            alpha = 10 if (y // 8) % 2 == 0 else 6
            pygame.draw.line(overlay, (255, 255, 255, alpha), (0, y), (WIDTH, y))
        surface.blit(overlay, (0, 0))


def run_game():
    """Run the main game loop. Returns True to return to the menu, False to quit."""
    os.environ.setdefault("SDL_VIDEO_WINDOW_POS", "100,100")
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Water Gun Game")

    font = _choose_font(36, bold=True)
    small_font = _choose_font(24)

    # toast list and helper
    toast_list = []
    def show_toast(text, duration_ms=1500, toasts=None):
        container = toast_list if toasts is None else toasts
        try:
            surf = small_font.render(text, True, WHITE)
        except Exception:
            surf = pygame.Surface((1, 1))
        expire = pygame.time.get_ticks() + duration_ms
        container.append({"surf": surf, "expire": expire})

    clock = pygame.time.Clock()
    player_score, computer_score = load_scores()
    round_count = 0
    game_over = False
    player_choice = None
    computer_choice = None
    result_text = ""

    click_anim = {"Snake": 0, "Water": 0, "Gun": 0}
    current_scale = {"Snake": 1.0, "Water": 1.0, "Gun": 1.0}
    target_scale = {"Snake": 1.0, "Water": 1.0, "Gun": 1.0}

    IMG_W, IMG_H = 150, 150
    snake_img = water_img = gun_img = None
    try:
        snake_img = pygame.transform.scale(pygame.image.load("snake.jpg"), (IMG_W, IMG_H))
        water_img = pygame.transform.scale(pygame.image.load("water.jpg"), (IMG_W, IMG_H))
        gun_img = pygame.transform.scale(pygame.image.load("gun.jpg"), (IMG_W, IMG_H))
    except Exception:
        pass

    WIN_COMMENTS = ["Nice! You beat the computer!", "Winner winner! Well played.", "You're on fire!", "Great move!"]
    LOSE_COMMENTS = ["Oh no — the computer got you.", "Tough luck, try again!", "The computer wins this round.", "Close one — better luck next time."]
    TIE_COMMENTS = ["It's a tie — evenly matched!", "Stalemate, try something different.", "Nobody wins this time.", "Tie game!"]

    running = True
    _auto_accum = 0
    _auto_interval = 800

    while running:
        dt = clock.tick(FPS)
        _auto_accum += dt

        if AUTO_PLAY and not game_over and _auto_accum >= _auto_interval:
            _auto_accum = 0
            player_choice = random.choice(["Snake", "Water", "Gun"])
            click_anim[player_choice] = 6
            computer_choice = random.choice(["Snake", "Water", "Gun"])
            result_text = get_winner(player_choice, computer_choice)
            if result_text == "You Win!":
                player_score += 1
                comment = random.choice(WIN_COMMENTS)
            elif result_text == "Computer Wins!":
                computer_score += 1
                comment = random.choice(LOSE_COMMENTS)
            else:
                comment = random.choice(TIE_COMMENTS)
            round_count += 1
            save_scores(player_score, computer_score)
            show_toast(comment)
            speak_async(comment)
            if round_count >= ROUND_LIMIT:
                game_over = True
                result_text = "GAME OVER"
                if player_score > computer_score:
                    speak_async("Congratulations! You won the game!")
                elif computer_score > player_score:
                    speak_async("Game Over! The computer wins!")
                else:
                    speak_async("Game Over! It's a tie!")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return True
                if event.key == pygame.K_r:
                    player_score = computer_score = 0
                    save_scores(0, 0)
                    show_toast("Scores reset")
                if event.key == pygame.K_v:
                    nonlocal_voice = globals()
                    globals()['VOICE_ENABLED'] = not globals().get('VOICE_ENABLED', True)
                    show_toast("Voice on" if globals().get('VOICE_ENABLED') else "Voice off")
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mx, my = event.pos
                snake_button = pygame.Rect(50, 150, IMG_W, IMG_H)
                water_button = pygame.Rect(225, 150, IMG_W, IMG_H)
                gun_button = pygame.Rect(400, 150, IMG_W, IMG_H)
                restart_button = pygame.Rect(WIDTH//2 - 90, HEIGHT - 70, 180, 50)

                if restart_button.collidepoint((mx, my)):
                    now = pygame.time.get_ticks()
                    active_confirm = None
                    for t in toast_list:
                        if t.get('restart_confirm') and t.get('expire', 0) > now:
                            active_confirm = t
                            break
                    if active_confirm:
                        round_count = 0
                        player_score = computer_score = 0
                        save_scores(0, 0)
                        game_over = False
                        result_text = "Game restarted"
                        player_choice = computer_choice = None
                        for k in click_anim:
                            click_anim[k] = 0
                            current_scale[k] = target_scale[k] = 1.0
                        toast_list[:] = [t for t in toast_list if not t.get('restart_confirm')]
                        show_toast("Game restarted")
                    else:
                        show_toast("Click Restart again to confirm", 2000)
                        toast_list.append({"restart_confirm": True, "expire": pygame.time.get_ticks() + 2000})
                else:
                    if snake_button.collidepoint((mx, my)):
                        player_choice = "Snake"
                    elif water_button.collidepoint((mx, my)):
                        player_choice = "Water"
                    elif gun_button.collidepoint((mx, my)):
                        player_choice = "Gun"

                    if player_choice:
                        click_anim[player_choice] = 6
                        computer_choice = random.choice(["Snake", "Water", "Gun"])
                        result_text = get_winner(player_choice, computer_choice)
                        if result_text == "You Win!":
                            player_score += 1
                            comment = random.choice(WIN_COMMENTS)
                        elif result_text == "Computer Wins!":
                            computer_score += 1
                            comment = random.choice(LOSE_COMMENTS)
                        else:
                            comment = random.choice(TIE_COMMENTS)
                        round_count += 1
                        save_scores(player_score, computer_score)
                        show_toast(comment)
                        speak_async(comment)
                        if round_count >= ROUND_LIMIT:
                            game_over = True
                            result_text = "GAME OVER"
                            if player_score > computer_score:
                                speak_async("Congratulations! You won the game!")
                            elif computer_score > player_score:
                                speak_async("Game Over! The computer wins!")
                            else:
                                speak_async("Game Over! It's a tie!")

        # draw
        draw_background(screen)
        snake_button = pygame.Rect(50, 150, IMG_W, IMG_H)
        water_button = pygame.Rect(225, 150, IMG_W, IMG_H)
        gun_button = pygame.Rect(400, 150, IMG_W, IMG_H)
        restart_button = pygame.Rect(WIDTH//2 - 90, HEIGHT - 70, 180, 50)

        mx, my = pygame.mouse.get_pos()
        hover_snake = snake_button.collidepoint((mx, my))
        hover_water = water_button.collidepoint((mx, my))
        hover_gun = gun_button.collidepoint((mx, my))
        hover_restart = restart_button.collidepoint((mx, my))

        target_scale['Snake'] = 1.08 if hover_snake else 1.0
        target_scale['Water'] = 1.08 if hover_water else 1.0
        target_scale['Gun'] = 1.08 if hover_gun else 1.0

        def _draw_choice(img, center, kind):
            if click_anim[kind] > 0:
                click_anim[kind] -= 1
                tgt = 0.86
            else:
                tgt = target_scale[kind]
            current_scale[kind] += (tgt - current_scale[kind]) * 0.25
            if img:
                im = pygame.transform.rotozoom(img, 0, current_scale[kind])
                rect = im.get_rect(center=center)
                shadow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                pygame.draw.ellipse(shadow, (0, 0, 0, 110), shadow.get_rect())
                screen.blit(shadow, (rect.x + 6, rect.y + rect.h//2 + 8))
                screen.blit(im, rect.topleft)
                return rect
            else:
                rect = pygame.Rect(0, 0, IMG_W, IMG_H)
                rect.center = center
                pygame.draw.rect(screen, (200, 200, 200), rect)
                return rect

        _draw_choice(snake_img, (50 + IMG_W//2, 150 + IMG_H//2), 'Snake')
        _draw_choice(water_img, (225 + IMG_W//2, 150 + IMG_H//2), 'Water')
        _draw_choice(gun_img, (400 + IMG_W//2, 150 + IMG_H//2), 'Gun')

        if hover_snake:
            pygame.draw.rect(screen, YELLOW, snake_button, 4)
        if hover_water:
            pygame.draw.rect(screen, YELLOW, water_button, 4)
        if hover_gun:
            pygame.draw.rect(screen, YELLOW, gun_button, 4)

        screen.blit(font.render('Snake', True, WHITE if hover_snake else RED), (50, 175))
        screen.blit(font.render('Water', True, WHITE if hover_water else RED), (225, 175))
        screen.blit(font.render('Gun', True, WHITE if hover_gun else RED), (445, 175))

        screen.blit(font.render(f'Score - You: {player_score}', True, BLUE), (10, 10))
        screen.blit(font.render(f'Computer: {computer_score}', True, BLUE), (350, 10))
        screen.blit(font.render(f'Round: {round_count}/{ROUND_LIMIT}', True, BLACK), (240, 50))
        screen.blit(small_font.render('Press R to reset scores, V to toggle voice', True, BLACK), (10, HEIGHT - 28))

        pygame.draw.rect(screen, LIGHT_GREEN if hover_restart else GREEN, restart_button)
        screen.blit(font.render('Restart Game', True, WHITE), restart_button.move(20, 10))

        if player_choice:
            screen.blit(font.render(f'You: {player_choice}', True, BLACK), (50, 50))
            screen.blit(font.render(f'Computer: {computer_choice}', True, BLACK), (300, 80))
            screen.blit(font.render(result_text, True, BLACK), (220, 300))

        if game_over:
            go_text = font.render('GAME OVER', True, RED)
            screen.blit(go_text, ((WIDTH - go_text.get_width())//2, HEIGHT//2 - 80))

        now = pygame.time.get_ticks()
        new_toasts = []
        ty = 8
        for t in toast_list:
            if t.get('restart_confirm'):
                if t['expire'] > now:
                    surf = small_font.render('Restart: click Restart again to confirm', True, WHITE)
                    screen.blit(surf, ((WIDTH - surf.get_width())//2, ty))
                    ty += surf.get_height() + 6
                    new_toasts.append(t)
                continue
            if t['expire'] > now:
                surf = t['surf'].copy()
                alpha = int(max(0, min(255, (t['expire'] - now) / 1500.0 * 255)))
                surf.set_alpha(alpha)
                screen.blit(surf, ((WIDTH - surf.get_width())//2, ty))
                ty += surf.get_height() + 6
                new_toasts.append(t)
        toast_list[:] = new_toasts

        pygame.display.flip()

    # Wait for voice to finish before quitting the demo window to avoid crashes
    try:
        voice.wait_until_done(timeout=3.0)
    except Exception:
        pass

    pygame.quit()
    return True


def run_demo():
    """Play a short animated demo of one automatic round, then return to the menu."""
    os.environ.setdefault("SDL_VIDEO_WINDOW_POS", "120,120")
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Water Gun - Demo")

    font = _choose_font(36, bold=True)
    small_font = _choose_font(20)

    IMG_W, IMG_H = 140, 140
    snake_img = water_img = gun_img = None
    try:
        snake_img = pygame.transform.scale(pygame.image.load("snake.jpg"), (IMG_W, IMG_H))
        water_img = pygame.transform.scale(pygame.image.load("water.jpg"), (IMG_W, IMG_H))
        gun_img = pygame.transform.scale(pygame.image.load("gun.jpg"), (IMG_W, IMG_H))
    except Exception:
        pass

    choices = ["Snake", "Water", "Gun"]
    player_choice = random.choice(choices)
    computer_choice = random.choice(choices)

    clock = pygame.time.Clock()
    elapsed = 0
    reveal_after = 1200  # ms to reveal final choices
    cycle_interval = 120
    last_cycle = 0
    disp_player = None
    disp_computer = None
    running = True
    revealed = False

    comment = None

    while running:
        dt = clock.tick(FPS)
        elapsed += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return True

        # cycle display choices until reveal
        if not revealed:
            last_cycle += dt
            if last_cycle >= cycle_interval:
                last_cycle = 0
                disp_player = random.choice(choices)
                disp_computer = random.choice(choices)
            if elapsed >= reveal_after:
                revealed = True
                disp_player = player_choice
                disp_computer = computer_choice
                # compute result and comment
                result_text = get_winner(player_choice, computer_choice)
                if result_text == "You Win!":
                    comment = random.choice(["Nice demo win!", "You beat the computer!"])
                elif result_text == "Computer Wins!":
                    comment = random.choice(["Computer wins this demo.", "The computer got it."])
                else:
                    comment = random.choice(["It's a demo tie!", "Demo ended in a tie."])
                # speak and prepare to show result
                # Use synchronous speak here to avoid background-thread/process races
                try:
                    voice.speak_sync(comment, voice_enabled=globals().get('VOICE_ENABLED', True))
                except Exception:
                    # Fallback to async queue if sync fails
                    speak_async(comment)
                reveal_show_time = 1800
                reveal_start = pygame.time.get_ticks()

        # draw
        draw_background(screen)

        # draw choices positions
        cx_player = (WIDTH//4, HEIGHT//2)
        cx_computer = (3*WIDTH//4, HEIGHT//2)

        def _draw_label(kind, center, img):
            if img:
                rect = img.get_rect(center=center)
                screen.blit(img, rect.topleft)
            else:
                surf = font.render(kind, True, (240, 240, 240))
                rect = surf.get_rect(center=center)
                screen.blit(surf, rect.topleft)

        if disp_player:
            img = snake_img if disp_player == 'Snake' else (water_img if disp_player == 'Water' else gun_img)
            _draw_label(disp_player, cx_player, img)
        if disp_computer:
            img = snake_img if disp_computer == 'Snake' else (water_img if disp_computer == 'Water' else gun_img)
            _draw_label(disp_computer, cx_computer, img)

        # labels
        screen.blit(small_font.render('Player (Demo)', True, WHITE), (cx_player[0]-70, cx_player[1]+90))
        screen.blit(small_font.render('Computer', True, WHITE), (cx_computer[0]-50, cx_computer[1]+90))

        if revealed and comment:
            # show result text until timeout then exit
            surf = font.render(comment, True, (255, 220, 120))
            screen.blit(surf, ((WIDTH - surf.get_width())//2, HEIGHT//2 + 120))
            # also show who won
            result_surf = small_font.render(result_text, True, (200, 200, 255))
            screen.blit(result_surf, ((WIDTH - result_surf.get_width())//2, HEIGHT//2 + 160))
            if pygame.time.get_ticks() - reveal_start >= reveal_show_time:
                running = False

        pygame.display.flip()

    pygame.quit()
    return True


if __name__ == '__main__':
    while True:
        import menu
        action = menu.run_menu()
        if action != 'play':
            break
        if not run_game():
            break