from enum import Enum, auto

class GameState(Enum):
    CONFIG = auto()
    READY = auto()
    PLANT_PHASE = auto()
    DEFUSE_PHASE = auto()
    EXPLODED = auto()
    DEFUSED = auto()
    TIME_OUT = auto() # Failed to plant in time

class StateMachine:
    def __init__(self):
        self.state = GameState.CONFIG
        self.plant_time = 0
        self.defuse_time = 0
        self.current_timer = 0
        
    def set_times(self, plant, defuse):
        self.plant_time = plant
        self.defuse_time = defuse
        
    def transition_to(self, new_state):
        self.state = new_state
        if new_state == GameState.PLANT_PHASE:
            self.current_timer = self.plant_time
        elif new_state == GameState.DEFUSE_PHASE:
            self.current_timer = self.defuse_time
            
    def tick(self, dt):
        """Seconds passed"""
        if self.state in [GameState.PLANT_PHASE, GameState.DEFUSE_PHASE]:
            self.current_timer -= dt
            if self.current_timer <= 0:
                self.current_timer = 0
                if self.state == GameState.PLANT_PHASE:
                    self.transition_to(GameState.TIME_OUT)
                elif self.state == GameState.DEFUSE_PHASE:
                    self.transition_to(GameState.EXPLODED)
                    
    def get_time_string(self):
        m = int(self.current_timer // 60)
        s = int(self.current_timer % 60)
        return f"{m:02d}:{s:02d}"
