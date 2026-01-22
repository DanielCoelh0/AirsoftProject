from enum import Enum, auto

class GameState(Enum):
    BOOT = auto()
    PIN_TYPE_SELECT = auto()
    PLAYER_REGISTRATION = auto()
    CONFIG = auto()
    READY = auto()
    PLANT_PHASE = auto()
    DEFUSE_PHASE = auto()
    EXPLODED = auto()
    DEFUSED = auto()
    TIME_OUT = auto() # Failed to plant in time

class StateMachine:
    def __init__(self):
        self.state = GameState.BOOT
        self.plant_time = 0
        self.defuse_time = 0
        self.current_timer = 0
        self.pin_mode = 1 # 1 for Static, 2 for Dynamic
        self.player_phones = [] # List of phone numbers
        self.dynamic_pin = "" # PIN set during plant
        self.logs = [] # Last 10 console logs
        self.show_console = False # For PIN Type 2/3 overlay
        
    def set_times(self, plant, defuse):
        self.plant_time = plant
        self.defuse_time = defuse
        
    def transition_to(self, new_state):
        self.state = new_state
        self.show_console = False # Reset overlay on state change
        if new_state == GameState.BOOT:
            self.logs = [] # Clear logs on reboot/reset
        if new_state == GameState.PLANT_PHASE:
            self.current_timer = self.plant_time
        elif new_state == GameState.DEFUSE_PHASE:
            self.current_timer = self.defuse_time
            
    def log(self, message):
        """Add message to logs and keep only last 10"""
        self.logs.append(message)
        if len(self.logs) > 10:
            self.logs = self.logs[-10:]
        print(f"[CONSOLE] {message}")
            
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
        ms = int((self.current_timer % 1) * 1000)
        return f"{m:02d}:{s:02d}.{ms:03d}"
