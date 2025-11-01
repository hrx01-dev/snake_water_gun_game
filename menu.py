import os
import sys
import pygame

# --- Configuration ---
WIDTH, HEIGHT = 600, 400
FPS = 60

# Initialize Pygame
os.environ.setdefault("SDL_VIDEO_WINDOW_POS", "100,100")
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Water Gun - Menu")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
LIGHT_GREEN = (0, 200, 0)
PURPLE = (128, 0, 128)
LIGHT_PURPLE = (147, 112, 219)

def _choose_font(size, bold=False):
    """Pick a 'cool' font from common system fonts, falling back to the default."""
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

# Fonts
title_font = _choose_font(48, bold=True)
button_font = _choose_font(36, bold=True)
small_font = _choose_font(24)

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
        # Create a nice gradient if no background image
        top = (48, 0, 64)  # Dark purple
        bottom = (147, 112, 219)  # Light purple
        gradient = _create_vertical_gradient(WIDTH, HEIGHT, top, bottom)
        surface.blit(gradient, (0, 0))
        # Add subtle texture
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 8):
            alpha = 10 if (y // 8) % 2 == 0 else 6
            pygame.draw.line(overlay, (255, 255, 255, alpha), (0, y), (WIDTH, y))
        surface.blit(overlay, (0, 0))

def run_menu():
    global screen
    # Ensure pygame is initialized (it may have been quit by other screens)
    if not pygame.get_init():
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Water Gun - Menu")
    print('[menu] run_menu: pygame initialized, entering loop')
    clock = pygame.time.Clock()
    current_scale = {"play": 1.0, "demo": 1.0, "rules": 1.0, "quit": 1.0}
    target_scale = {"play": 1.0, "demo": 1.0, "rules": 1.0, "quit": 1.0}

    # Button dimensions and positions (Play, Demo, Rules, Quit)
    play_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 70, 200, 56)
    demo_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 10, 200, 52)
    rules_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 48)
    quit_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 56)

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if play_button.collidepoint((mx, my)):
                    pygame.quit()
                    return "play"
                elif demo_button.collidepoint((mx, my)):
                    # Demo -> return a special action to launcher
                    print('[menu] demo button clicked, returning demo')
                    pygame.quit()
                    return "demo"
                elif rules_button.collidepoint((mx, my)):
                    # Open rules screen; rules.run_rules() returns 'back'|'play'|'quit'
                    pygame.quit()
                    try:
                        import rules
                    except Exception:
                        # If rules module fails, return to menu
                        pygame.init()
                        continue
                    action = rules.run_rules()
                    if action == 'play':
                        return 'play'
                    elif action == 'quit':
                        sys.exit()
                    else:
                        # back -> reopen menu display
                        pygame.init()
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                        pygame.display.set_caption("Snake Water Gun - Menu")
                        continue
                elif quit_button.collidepoint((mx, my)):
                    pygame.quit()
                    sys.exit()

        # Draw background
        draw_background(screen)

        # Draw title
        title = title_font.render("Snake Water Gun", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
        screen.blit(title, title_rect)

        # Get mouse position for hover effects
        mx, my = pygame.mouse.get_pos()
        hover_play = play_button.collidepoint((mx, my))
        hover_demo = demo_button.collidepoint((mx, my))
        hover_rules = rules_button.collidepoint((mx, my))
        hover_quit = quit_button.collidepoint((mx, my))

        # Update button scales
        target_scale["play"] = 1.08 if hover_play else 1.0
        target_scale["demo"] = 1.06 if hover_demo else 1.0
        target_scale["rules"] = 1.06 if hover_rules else 1.0
        target_scale["quit"] = 1.08 if hover_quit else 1.0
        for key in current_scale:
            current_scale[key] += (target_scale[key] - current_scale[key]) * 0.25

        # Draw Play button with animation
        play_surface = pygame.Surface((play_button.width, play_button.height), pygame.SRCALPHA)
        scaled_play = pygame.transform.rotozoom(play_surface, 0, current_scale["play"])
        scaled_play_rect = scaled_play.get_rect(center=play_button.center)
        pygame.draw.rect(screen, LIGHT_GREEN if hover_play else GREEN, scaled_play_rect)
        play_text = button_font.render("PLAY", True, WHITE)
        screen.blit(play_text, play_text.get_rect(center=scaled_play_rect.center))

        # Draw Demo button
        demo_surface = pygame.Surface((demo_button.width, demo_button.height), pygame.SRCALPHA)
        scaled_demo = pygame.transform.rotozoom(demo_surface, 0, current_scale["demo"])
        scaled_demo_rect = scaled_demo.get_rect(center=demo_button.center)
        pygame.draw.rect(screen, (255, 180, 60) if hover_demo else (220, 140, 30), scaled_demo_rect)
        demo_text = button_font.render("DEMO", True, BLACK)
        screen.blit(demo_text, demo_text.get_rect(center=scaled_demo_rect.center))

        # Draw Rules button
        rules_surface = pygame.Surface((rules_button.width, rules_button.height), pygame.SRCALPHA)
        scaled_rules = pygame.transform.rotozoom(rules_surface, 0, current_scale["rules"])
        scaled_rules_rect = scaled_rules.get_rect(center=rules_button.center)
        pygame.draw.rect(screen, (200, 200, 120) if hover_rules else (180, 160, 80), scaled_rules_rect)
        rules_text = button_font.render("RULES", True, BLACK)
        screen.blit(rules_text, rules_text.get_rect(center=scaled_rules_rect.center))

        # Draw Quit button with animation
        quit_surface = pygame.Surface((quit_button.width, quit_button.height), pygame.SRCALPHA)
        scaled_quit = pygame.transform.rotozoom(quit_surface, 0, current_scale["quit"])
        scaled_quit_rect = scaled_quit.get_rect(center=quit_button.center)
        pygame.draw.rect(screen, LIGHT_PURPLE if hover_quit else PURPLE, scaled_quit_rect)
        quit_text = button_font.render("QUIT", True, WHITE)
        screen.blit(quit_text, quit_text.get_rect(center=scaled_quit_rect.center))

        # Draw credits at bottom
        credits = small_font.render("Created with ♥ by GitHub Copilot", True, WHITE)
        credits_rect = credits.get_rect(bottom=HEIGHT-10, centerx=WIDTH//2)
        screen.blit(credits, credits_rect)

        pygame.display.flip()

if __name__ == "__main__":
    action = run_menu()
    if action == "play":
        import main  # Start the main game