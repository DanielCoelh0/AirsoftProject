import pygame
from .. import config

class Renderer:
    def __init__(self):
        pygame.init()
        # 240x320 Portrait
        self.width = 240
        self.height = 320
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Airsoft Bomb")
        
        # Fonts
        self.font_header = pygame.font.SysFont("Arial", 30, bold=True)        
        self.font_large = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 25)
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.font_countdown = pygame.font.SysFont("Arial", 50, bold=True)

        
    def clear(self):
        self.screen.fill(config.COLOR_BLACK)
        
    def draw_console_overlay(self, logs):
        """Draw 80% transparent black overlay with log messages"""
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(204)  # ~80% transparency (255 * 0.8 = 204)
        overlay.fill(config.COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Border
        pygame.draw.rect(self.screen, config.COLOR_GREEN, (10, 10, self.width - 20, self.height - 20), 2)
        
        # Title
        self.draw_text("SYSTEM CONSOLE", self.font_medium, config.COLOR_GREEN, (self.width // 2, 30))
        
        # Draw Logs
        x_start = 20
        y_start = 60
        line_height = 20
        
        for i, log_msg in enumerate(logs):
            surface = self.font_small.render(f"> {log_msg}", True, config.COLOR_GREEN)
            self.screen.blit(surface, (x_start, y_start + i * line_height))

    def update(self):
        pygame.display.flip()
        
    def draw_text(self, text, font, color, center_pos):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(center_pos[0], center_pos[1]))
        self.screen.blit(surface, rect)
        
    def render(self, state_machine, current_input="", input_label="INPUT", screen_blink=False, text_blink=False, video_frame=None):
        self.clear()
        state = state_machine.state
        
        # Header (Top Bar)
        pygame.draw.rect(self.screen, (30, 30, 30), (0, 0, self.width, 40))

        # Content Area
        cx = self.width // 2
        cy = self.height // 2
        
        from ..state_machine import GameState
        
        if state == GameState.BOOT:
            # Display video frame (fullscreen, no header)
            if video_frame is not None:
                # video_frame is already a pygame surface, just blit it
                self.screen.blit(video_frame, (0, 0))
            else:
                # Fallback if no frame provided
                self.clear()
            return  # Skip header drawing for boot screen
        
        if state == GameState.PIN_TYPE_SELECT:
            self.draw_text("PIN MODE", self.font_header, config.COLOR_WHITE, (self.width//2, 20))
            self.draw_text("1: STATIC PIN", self.font_medium, config.COLOR_WHITE, (cx, 80))
            self.draw_text("2: DYNAMIC PIN", self.font_medium, config.COLOR_WHITE, (cx, 120))
            self.draw_text("3: TELEGRAM PIN", self.font_medium, config.COLOR_WHITE, (cx, 160))
            self.draw_text(f"CHOICE: {current_input}", self.font_large, config.COLOR_GREEN, (cx, 220))
            self.draw_text("PRESS # TO CONFIRM", self.font_small, config.COLOR_WHITE, (cx, 280))

        elif state == GameState.PLAYER_REGISTRATION:
            self.draw_text("REGISTRATION", self.font_header, config.COLOR_WHITE, (self.width//2, 20))
            self.draw_text(input_label, self.font_medium, config.COLOR_WHITE, (cx, 100))
            self.draw_text(current_input, self.font_large, config.COLOR_GREEN, (cx, 160))
            self.draw_text("PRESS # TO REGISTER", self.font_small, config.COLOR_WHITE, (cx, 240))
            self.draw_text("PRESS * TO FINISH", self.font_small, config.COLOR_WHITE, (cx, 270))
            # Show small list of already registered?
            count = len(state_machine.player_phones)
            self.draw_text(f"REGISTERED: {count}", self.font_small, config.COLOR_YELLOW, (cx, 300))

        elif state == GameState.CONFIG:
            # Header text
            self.draw_text("GAME SETUP", self.font_header, config.COLOR_WHITE, (self.width//2, 20))
            # Content Area
            self.draw_text(f"PLANT TIME: {state_machine.plant_time}s", self.font_medium, config.COLOR_WHITE, (cx, 80))
            self.draw_text(f"DEFUSE TIME: {state_machine.defuse_time}s", self.font_medium, config.COLOR_WHITE, (cx, 120))
            self.draw_text(f"{input_label}", self.font_medium, config.COLOR_GREEN, (cx, 170))
            self.draw_text(f"{current_input}", self.font_large, config.COLOR_GREEN, (cx, 220))
            self.draw_text("PRESS # TO CONFIRM", self.font_small, config.COLOR_WHITE, (cx, 270))
            self.draw_text("HOLD # (2s) TO RESET", self.font_small, (100, 100, 100), (cx, 300))
            
        elif state == GameState.READY:
            # Header text
            self.draw_text("GAME READY", self.font_header, config.COLOR_GREEN, (self.width//2, 20))
            # Content Area
            self.draw_text("PRESS * TO START", self.font_medium, config.COLOR_WHITE, (cx, cy - 30))
            self.draw_text("START", self.font_large, config.COLOR_WHITE, (cx, cy + 30))
            self.draw_text("HOLD # (2s) TO RESET", self.font_small, (100, 100, 100), (cx, 300))
            
        elif state == GameState.PLANT_PHASE:
            # Screen blink effect (yellow overlay)
            if screen_blink:
                overlay = pygame.Surface((self.width, self.height))
                overlay.set_alpha(80)  # Semi-transparent
                overlay.fill(config.COLOR_YELLOW)
                self.screen.blit(overlay, (0, 0))
            
            # Header text
            self.draw_text("PLANT BOMB", self.font_header, config.COLOR_YELLOW, (self.width//2, 20))
            # Content Area
            time_str = state_machine.get_time_string() # Timer
            self.draw_text(time_str, self.font_countdown, config.COLOR_WHITE, (cx, cy - 60))
            self.draw_text("TO DEADLINE", self.font_medium, config.COLOR_YELLOW, (cx, cy))
            self.draw_text("PRESS * TO ENTER CODE", self.font_small, config.COLOR_WHITE, (cx, cy + 60))
            self.draw_text(current_input, self.font_large, config.COLOR_YELLOW, (cx, cy + 120))
            
        elif state == GameState.DEFUSE_PHASE:
            # Screen blink effect (red overlay)
            if screen_blink:
                overlay = pygame.Surface((self.width, self.height))
                overlay.set_alpha(80)  # Semi-transparent
                overlay.fill(config.COLOR_RED)
                self.screen.blit(overlay, (0, 0))
            
            # Header text
            self.draw_text("ARMED!", self.font_header, config.COLOR_RED, (self.width//2, 20))
            # Content Area
            time_str = state_machine.get_time_string()
            self.draw_text(time_str, self.font_countdown, config.COLOR_RED, (cx, cy - 60))
            self.draw_text("TO KABOOM", self.font_medium, config.COLOR_YELLOW, (cx, cy))
            self.draw_text(f"{input_label}", self.font_small, config.COLOR_WHITE, (cx, cy + 60))
            self.draw_text(current_input, self.font_large, config.COLOR_WHITE, (cx, cy + 120))

        elif state == GameState.EXPLODED:
            # Header text
            self.draw_text("BOOM!", self.font_header, config.COLOR_RED, (self.width//2, 20))
            # Content Area
            self.draw_text("TARGET", self.font_large, config.COLOR_RED, (cx, cy - 60))
            if not text_blink:  # Only show when not blinking (creates blink effect)
                self.draw_text("DESTROYED", self.font_large, config.COLOR_RED, (cx, cy))
            self.draw_text("MASKS OFF!", self.font_small, config.COLOR_WHITE, (cx, cy + 60))
            
        elif state == GameState.DEFUSED:
            # Header text
            self.draw_text("DEFUSED!", self.font_header, config.COLOR_RED, (self.width//2, 20))
            # Content Area
            self.draw_text("MISSION", self.font_large, config.COLOR_GREEN, (cx, cy - 60))
            if not text_blink:  # Only show when not blinking (creates blink effect)
                self.draw_text("SUCCESS", self.font_large, config.COLOR_GREEN, (cx, cy))
            self.draw_text("COUNTER-TERRORISTS WIN", self.font_small, config.COLOR_WHITE, (cx, cy + 60))

        elif state == GameState.TIME_OUT:
            # Header text
            self.draw_text("TIME OUT!", self.font_header, config.COLOR_RED, (self.width//2, 20))
            # Content Area  
            self.draw_text("TERRORISTS", self.font_medium, config.COLOR_YELLOW, (cx, cy - 60))
            if not text_blink:  # Only show when not blinking (creates blink effect)
                self.draw_text("FAILED", self.font_large, config.COLOR_YELLOW, (cx, cy))
            self.draw_text("TRY RUSH B", self.font_small, config.COLOR_WHITE, (cx, cy + 60))
            
        if state in [GameState.EXPLODED, GameState.DEFUSED, GameState.TIME_OUT]:
            self.draw_text("PRESS # TO PLAY AGAIN", self.font_small, config.COLOR_WHITE, (cx, 270))
            self.draw_text("HOLD # (2s) TO RESET", self.font_small, (100, 100, 100), (cx, 300))
        
        # PIN TYPE 2/3 CONSOLE OVERLAY
        if state_machine.show_console:
            self.draw_console_overlay(state_machine.logs)
