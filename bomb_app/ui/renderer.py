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

        
    def clear(self):
        self.screen.fill(config.COLOR_BLACK)
        
    def update(self):
        pygame.display.flip()
        
    def draw_text(self, text, font, color, center_pos):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(center_pos[0], center_pos[1]))
        self.screen.blit(surface, rect)
        
    def render(self, state_machine, current_input="", input_label="INPUT"):
        self.clear()
        state = state_machine.state
        
        # Header (Top Bar)
        pygame.draw.rect(self.screen, (30, 30, 30), (0, 0, self.width, 40))

        # Content Area
        cx = self.width // 2
        cy = self.height // 2
        
        from ..state_machine import GameState
        
        if state == GameState.CONFIG:
            # Header text
            self.draw_text("GAME SETUP", self.font_header, config.COLOR_WHITE, (self.width//2, 20))
            # Content Area
            self.draw_text(f"PLANT TIME: {state_machine.plant_time}s", self.font_small, config.COLOR_WHITE, (cx, 100))
            self.draw_text(f"DEFUSE TIME: {state_machine.defuse_time}s", self.font_small, config.COLOR_WHITE, (cx, 130))
            self.draw_text("TYPE TIME AND PRESS #", self.font_small, (100, 100, 100), (cx, 160))
            self.draw_text(f"{input_label}: {current_input}", self.font_medium, config.COLOR_GREEN, (cx, 200))
            self.draw_text("PRESS # TO CONFIRM", self.font_small, config.COLOR_WHITE, (cx, 270))
            self.draw_text("HOLD # (2s) TO RESET", self.font_small, (100, 100, 100), (cx, 300))
            
        elif state == GameState.READY:
            self.draw_text("READY", self.font_large, config.COLOR_GREEN, (cx, cy - 20))
            self.draw_text("PRESS * TO START", self.font_medium, config.COLOR_WHITE, (cx, cy + 30))
            self.draw_text("HOLD # (2s) TO RESET", self.font_small, (100, 100, 100), (cx, 300))
            
        elif state == GameState.PLANT_PHASE:
            self.draw_text("PLANTING", self.font_large, config.COLOR_RED, (cx, 80))
            
            # Timer
            time_str = state_machine.get_time_string()
            self.draw_text(time_str, self.font_large, config.COLOR_WHITE, (cx, 140))
            
            self.draw_text("PRESS * TO ENTER CODE", self.font_small, config.COLOR_WHITE, (cx, 200))
            self.draw_text(current_input, self.font_large, config.COLOR_YELLOW, (cx, 240))
            
        elif state == GameState.DEFUSE_PHASE:
            self.draw_text("ARMED!", self.font_large, config.COLOR_RED, (cx, 60))
            self.draw_text("DEFUSE NOW", self.font_small, config.COLOR_YELLOW, (cx, 90))
            self.draw_text("PRESS * TO ENTER CODE", self.font_small, config.COLOR_WHITE, (cx, 200))
            
            # Blink effect for timer maybe?
            time_str = state_machine.get_time_string()
            self.draw_text(time_str, self.font_large, config.COLOR_RED, (cx, 150))
            
            self.draw_text(current_input, self.font_large, config.COLOR_WHITE, (cx, 240))

        elif state == GameState.EXPLODED:
            self.draw_text("BOOM!", self.font_large, config.COLOR_RED, (cx, cy))
            self.draw_text("MASKS OFF!", self.font_small, config.COLOR_WHITE, (cx, cy + 60))
            
        elif state == GameState.DEFUSED:
            self.draw_text("BOMB", self.font_large, config.COLOR_GREEN, (cx, cy - 20))
            self.draw_text("DEFUSED", self.font_large, config.COLOR_GREEN, (cx, cy + 20))
            self.draw_text("COUNTER-TERRORISTS WIN", self.font_small, config.COLOR_WHITE, (cx, cy + 60))

        elif state == GameState.TIME_OUT:
            self.draw_text("TIME OUT", self.font_large, config.COLOR_YELLOW, (cx, cy - 20))
            self.draw_text("PLANT FAILED", self.font_small, config.COLOR_WHITE, (cx, cy + 20))
            
        if state in [GameState.EXPLODED, GameState.DEFUSED, GameState.TIME_OUT]:
            self.draw_text("PRESS # TO PLAY AGAIN", self.font_small, (150, 150, 150), (cx, 270))
            self.draw_text("HOLD # (2s) TO RESET", self.font_small, (100, 100, 100), (cx, 300))
