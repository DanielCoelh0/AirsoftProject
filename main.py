
import pygame
import sys
from bomb_app import config, state_machine
from bomb_app.hardware import get_hardware
from bomb_app.ui.renderer import Renderer

def main():
    hw = get_hardware()
    hw.initialize()
    renderer = Renderer()
    sm = state_machine.StateMachine()
    
    # State Helpers
    config_step = 0 # 0=Plant, 1=Defuse
    input_buffer = ""
    showing_input = False # For Plant/Defuse phases, do we show input field?
    message_overlay = "" # For "WRONG CODE" etc.
    message_timer = 0
    
    clock = pygame.time.Clock()
    running = True
    
    last_keys = set()
    hash_hold_time = 0
    
    # Initialize defaults
    sm.set_times(config.DEFAULT_PLANT_TIME, config.DEFAULT_DEFUSE_TIME)
    
    while running:
        dt = clock.tick(30) / 1000.0
        
        # --- INPUT HANDLING (PYGAME + MOCK INJECTION) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Key Injection for Mock Hardware
            if hasattr(hw, 'set_key_state'):
                is_down = (event.type == pygame.KEYDOWN)
                key = None
                if event.key == pygame.K_KP0 or event.key == pygame.K_0: key = '0'
                if event.key == pygame.K_KP1 or event.key == pygame.K_1: key = '1'
                if event.key == pygame.K_KP2 or event.key == pygame.K_2: key = '2'
                if event.key == pygame.K_KP3 or event.key == pygame.K_3: key = '3'
                if event.key == pygame.K_KP4 or event.key == pygame.K_4: key = '4'
                if event.key == pygame.K_KP5 or event.key == pygame.K_5: key = '5'
                if event.key == pygame.K_KP6 or event.key == pygame.K_6: key = '6'
                if event.key == pygame.K_KP7 or event.key == pygame.K_7: key = '7'
                if event.key == pygame.K_KP8 or event.key == pygame.K_8: key = '8'
                if event.key == pygame.K_KP9 or event.key == pygame.K_9: key = '9'
                if event.key == pygame.K_KP_MULTIPLY or event.key == pygame.K_8 and (pygame.key.get_mods() & pygame.KMOD_SHIFT): key = '*' # Shift+8 is *
                if event.key == pygame.K_BACKSPACE: # Debug helper
                    input_buffer = input_buffer[:-1]
                
                # Handling '#' mapping: Enter or Shift+3
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER: key = '#'
                if event.key == pygame.K_3 and (pygame.key.get_mods() & pygame.KMOD_SHIFT): key = '#'

                if key:
                    hw.set_key_state(key, is_down)

        # --- HARDWARE POLL ---
        current_keys = set(hw.get_pressed_keys())
        just_pressed = current_keys - last_keys
        last_keys = current_keys
        
        # --- GLOBAL LOGIC (Hold # to Config) ---
        if '#' in current_keys:
            hash_hold_time += dt
            if hash_hold_time > 2.0:
                 # LONG PRESS RESET
                 sm.transition_to(state_machine.GameState.CONFIG)
                 config_step = 0
                 input_buffer = str(sm.plant_time)
                 hash_hold_time = 0
                 message_overlay = "RESETting..."
                 message_timer = 1.0
        else:
            hash_hold_time = 0

        # --- STATE LOGIC ---
        sm.tick(dt)
        
        # Message overlay timer
        if message_timer > 0:
            message_timer -= dt
            if message_timer <= 0:
                message_overlay = ""

        # Handle Key Presses
        for key in just_pressed:
            if message_timer > 0: # Clear message on any key
                message_overlay = ""
                # Optional: return/continue to prevent input during message?
            
            # BEEP on press
            hw.beep(50)
            
            if sm.state == state_machine.GameState.CONFIG:
                if key.isdigit():
                    input_buffer += key
                elif key == '*':
                    input_buffer = "" # Clear
                elif key == '#':
                    # Confirm
                    val = int(input_buffer) if input_buffer else 0
                    if config_step == 0: # Plant Time
                        sm.plant_time = val
                        config_step = 1
                        input_buffer = str(sm.defuse_time)
                    else: # Defuse Time
                        sm.defuse_time = val
                        sm.transition_to(state_machine.GameState.READY)
                        input_buffer = ""
            
            elif sm.state == state_machine.GameState.READY:
                if key == '*':
                    sm.transition_to(state_machine.GameState.PLANT_PHASE)
                    input_buffer = ""
                    showing_input = False
            
            elif sm.state == state_machine.GameState.PLANT_PHASE:
                # "To arm ... press *, screen ask for arm pin"
                if not showing_input:
                    if key == '*':
                        showing_input = True
                        input_buffer = ""
                else: 
                    # Showing Input for Arming
                    if key.isdigit():
                        input_buffer += key
                        if len(input_buffer) == 4:
                            # Auto check on 4 digits or wait for #? Req says "User press 1234 and bomb will be armed" -> implied auto or manual?
                            # "any other code must show WRONG CODE"
                            if input_buffer == config.ARM_PIN:
                                sm.transition_to(state_machine.GameState.DEFUSE_PHASE)
                                showing_input = False
                                input_buffer = ""
                            else:
                                message_overlay = "WRONG CODE"
                                message_timer = 2.0
                                input_buffer = ""
                                showing_input = False 
                    elif key == '*': # Cancel input?
                        showing_input = False

            elif sm.state == state_machine.GameState.DEFUSE_PHASE:
                # "To defuse ... press *, screen ask for pin"
                if not showing_input:
                    if key == '*':
                        showing_input = True
                        input_buffer = ""
                else:
                    if key.isdigit():
                        input_buffer += key
                        if len(input_buffer) == 4:
                            if input_buffer == config.DEFUSE_PIN:
                                sm.transition_to(state_machine.GameState.DEFUSED)
                            else:
                                message_overlay = "WRONG CODE"
                                message_timer = 2.0
                                input_buffer = ""
                                showing_input = False
                    elif key == '*': # Cancel
                        showing_input = False
                        
            elif sm.state in [state_machine.GameState.EXPLODED, state_machine.GameState.DEFUSED, state_machine.GameState.TIME_OUT]:
                if key == '#':
                    # Short press -> Ready
                    sm.transition_to(state_machine.GameState.READY)

        # --- RENDER ---
        # Modify render call to pass extra state info (overlay, waiting_for_pin)
        # We need to adapt the Renderer class or hack it here by passing a composite object or doing render logic inside Renderer
        # For simplicity, I'll pass input_buffer if showing_input is True, else empty
        
        display_input = input_buffer if showing_input or sm.state == state_machine.GameState.CONFIG else ""
        
        # Pass extra context to renderer?
        # A simpler way is to handle text drawing here or update renderer to accept 'overlay_text'.
        # Let's update Renderer.render signature in next step or now?
        # I'll rely on renderer.render handling basic state. 
        # I need to render 'message_overlay' if present.
        
        renderer.render(sm, display_input)
        
        if message_overlay:
            renderer.draw_text(message_overlay, renderer.font_large, config.COLOR_RED, (renderer.width//2, renderer.height//2))
            
        if sm.state == state_machine.GameState.CONFIG:
             # Show which config step
             step_name = "Set PLANT Time" if config_step == 0 else "Set DEFUSE Time"
             renderer.draw_text(step_name, renderer.font_small, config.COLOR_RED, (renderer.width//2, 30))

        renderer.update()

    hw.cleanup()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
