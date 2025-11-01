import sys

"""Launcher for Snake Water Gun game.
Delegates to `menu.py` for the main menu and `game.py` for the gameplay.
Run this file to start the menu.
"""

if __name__ == "__main__":
    # Loop: show menu, run game if requested
    while True:
        try:
            import menu
        except Exception as e:
            print("Failed to import menu:", e)
            raise
        action = menu.run_menu()
        if action == "demo":
            try:
                import game
            except Exception as e:
                print("Failed to import game for demo:", e)
                raise
            back_to_menu = game.run_demo()
            if not back_to_menu:
                break
            # return to menu loop
            continue
        if action != "play":
            break
        try:
            import game
        except Exception as e:
            print("Failed to import game:", e)
            raise
        # run_game returns True to go back to menu, False to quit
        back_to_menu = game.run_game()
        if not back_to_menu:
            break
    sys.exit(0)