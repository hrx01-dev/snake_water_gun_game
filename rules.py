import os
import sys
import pygame

# Reuse same sizing as menu/game
WIDTH, HEIGHT = 600, 400
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
LIGHT_GREEN = (0, 200, 0)
PURPLE = (128, 0, 128)


def _choose_font(size, bold=False):
    candidates = ["Montserrat", "Segoe UI", "Impact", "Arial Black", "Calibri", "Verdana", "Arial", "Tahoma"]
    for name in candidates:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f and f.size("A"):
                return f
        except Exception:
            continue
    return pygame.font.Font(None, size)


title_font = None
body_font = None
button_font = None


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
        top = (24, 48, 80)
        bottom = (100, 140, 200)
        surf = _create_vertical_gradient(WIDTH, HEIGHT, top, bottom)
        surface.blit(surf, (0, 0))


def run_rules():
    """Display rules screen. Returns one of: 'back', 'play', 'quit'."""
    global title_font, body_font, button_font
    os.environ.setdefault("SDL_VIDEO_WINDOW_POS", "100,100")
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Water Gun - Rules")

    title_font = _choose_font(40, bold=True)
    body_font = _choose_font(20)
    button_font = _choose_font(28, bold=True)

    play_button = pygame.Rect(WIDTH//2 - 100, HEIGHT - 110, 200, 48)
    back_button = pygame.Rect(20, HEIGHT - 60, 120, 40)

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return "back"
                elif event.key == pygame.K_p:
                    pygame.quit()
                    return "play"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if play_button.collidepoint((mx, my)):
                    pygame.quit()
                    return "play"
                if back_button.collidepoint((mx, my)):
                    pygame.quit()
                    return "back"

        draw_background(screen)

        title = title_font.render("How to play", True, WHITE)
        screen.blit(title, (20, 20))

        lines = [
            "Rules:",
            "- Snake beats Water (snake drinks water).",
            "- Water beats Gun (water rusts the gun).",
            "- Gun beats Snake (gun shoots snake).",
            "", 
            "Controls:",
            "- Click the Snake/Water/Gun images to choose.",
            "- Press R to reset scores, V to toggle voice.",
            "- Press ESC to return to the menu.",
            "", 
            "Objective:",
            "Win more rounds than the computer within 10 rounds."
        ]

        y = 80
        for l in lines:
            surf = body_font.render(l, True, WHITE)
            screen.blit(surf, (28, y))
            y += surf.get_height() + 6

        # Draw buttons
        mx, my = pygame.mouse.get_pos()
        hover_play = play_button.collidepoint((mx, my))
        hover_back = back_button.collidepoint((mx, my))

        pygame.draw.rect(screen, LIGHT_GREEN if hover_play else GREEN, play_button)
        play_text = button_font.render("PLAY", True, BLACK)
        screen.blit(play_text, play_text.get_rect(center=play_button.center))

        pygame.draw.rect(screen, (100, 100, 100) if hover_back else (80, 80, 80), back_button)
        back_text = button_font.render("BACK", True, WHITE)
        screen.blit(back_text, back_text.get_rect(center=back_button.center))

        pygame.display.flip()

    pygame.quit()
    return "back"
