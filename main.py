
import pygame
import sys
import cv2
import os
from bomb_app import config, state_machine
from bomb_app.hardware import get_hardware
from bomb_app.ui.renderer import Renderer
from bomb_app.telegram_config import TELEGRAM_CHAT_ID_TERRORISTS, TELEGRAM_CHAT_ID_COUNTERTERRORISTS

def load_video(video_path):
    """Load video and return VideoCapture object, or None if file doesn't exist"""
    if not os.path.exists(video_path):
        print(f"[WARNING] Boot video not found at: {video_path}")
        return None
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"[WARNING] Could not open video: {video_path}")
            return None
        return cap
    except Exception as e:
        print(f"[WARNING] Error loading video: {e}")
        return None

def get_video_frame(cap, frame_number):
    """Get a specific frame from video as pygame surface"""
    if cap is None:
        return None
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    if not ret:
        return None
    
    # Convert BGR to RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Resize to fit screen if needed (240x320 portrait)
    if frame.shape[1] != 240 or frame.shape[0] != 320:
        frame = cv2.resize(frame, (240, 320), interpolation=cv2.INTER_AREA)
    
    # Transpose for pygame (pygame expects width, height; opencv is height, width)
    # Swap axes: (height, width, channels) -> (width, height, channels)
    frame = frame.transpose((1, 0, 2))
    
    # Convert to pygame surface
    frame = pygame.surfarray.make_surface(frame)
    
    return frame


def main():
    hw = get_hardware()
    hw.initialize()
    renderer = Renderer()
    sm = state_machine.StateMachine()
    tg_chat_id_terrorists = TELEGRAM_CHAT_ID_TERRORISTS
    tg_chat_id_counterterrorists = TELEGRAM_CHAT_ID_COUNTERTERRORISTS
    
    # State Helpers
    config_step = 0 # 0=Plant, 1=Defuse
    player_step = 0 # For Player Registration index
    defuse_step = 0 # 0=Phone Number, 1=PIN
    input_buffer = ""
    showing_input = False # For Plant/Defuse phases, do we show input field?
    message_overlay = "" # For "WRONG CODE" etc.
    message_timer = 0
    
    clock = pygame.time.Clock()
    running = True
    
    last_keys = set()
    hash_hold_time = 0
    
    # Blink and Buzzer timing
    blink_timer = 0  # For screen/text blinking
    screen_blink_state = False  # Current blink state
    text_blink_state = False
    last_beep_time = -999  # Track last buzzer beep to prevent duplicates
    last_30s_mark = -1  # Track 30s interval beeps for PLANT_PHASE
    
    # Boot video
    boot_video = load_video(config.BOOT_VIDEO_PATH)
    current_video_frame = 0
    video_fps = 30  # Default FPS
    video_frame_time = 0  # Accumulator for frame timing
    video_ended = False
    video_last_frame = None  # Store last frame for freezing
    
    if boot_video is not None:
        video_fps = boot_video.get(cv2.CAP_PROP_FPS)
        if video_fps <= 0:
            video_fps = 30  # Fallback
        total_frames = int(boot_video.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"[INFO] Boot video loaded: {total_frames} frames at {video_fps} FPS")
    
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
                if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
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
                    if event.key == pygame.K_KP_MULTIPLY or (event.key == pygame.K_8 and (pygame.key.get_mods() & pygame.KMOD_SHIFT)): key = '*' # Shift+8 is *
                    if event.key == pygame.K_BACKSPACE and is_down: # Debug helper, only on down
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
                 sm.transition_to(state_machine.GameState.PIN_TYPE_SELECT)
                 config_step = 0
                 input_buffer = "" # Start blank per request
                 hash_hold_time = 0
                 message_overlay = "RESETting..."
                 message_timer = 1.0
                 # Reset timers
                 blink_timer = 0
                 last_beep_time = -999
                 last_30s_mark = -1
        else:
            hash_hold_time = 0

        # --- STATE LOGIC ---
        sm.tick(dt)
        
        # --- BUZZER AND BLINK LOGIC ---
        # Update blink timer
        blink_timer += dt
        
        # BOOT state: Video playback
        if sm.state == state_machine.GameState.BOOT:
            if boot_video is not None and not video_ended:
                # Advance video frame based on timing
                video_frame_time += dt
                frame_duration = 1.0 / video_fps
                
                if video_frame_time >= frame_duration:
                    video_frame_time = 0
                    current_video_frame += 1
                    
                    # Check if video ended
                    total_frames = int(boot_video.get(cv2.CAP_PROP_FRAME_COUNT))
                    if current_video_frame >= total_frames:
                        video_ended = True
                        current_video_frame = total_frames - 1  # Stay on last frame
                        
                        # Store last frame for display
                        video_last_frame = get_video_frame(boot_video, current_video_frame)
            
            # If no video file exists, auto-skip
            if boot_video is None:
                sm.transition_to(state_machine.GameState.PIN_TYPE_SELECT)
                input_buffer = ""
                # Reset timers
                blink_timer = 0
                last_beep_time = -999
                last_30s_mark = -1
        
        # Screen blink for PLANT_PHASE (every 1 second)
        if sm.state == state_machine.GameState.PLANT_PHASE:
            if blink_timer >= 1.0:
                screen_blink_state = not screen_blink_state
                blink_timer = 0
            
            # Buzzer beeps every 30s from finish
            remaining = sm.current_timer
            current_30s_mark = int(remaining // 30)
            if current_30s_mark != last_30s_mark and remaining % 30 < 0.1:  # At 30s intervals
                if remaining >= 3:  # Don't interfere with countdown beeps
                    hw.beep(100)
                    last_beep_time = remaining
                last_30s_mark = current_30s_mark
        
        # Screen blink and buzzer for DEFUSE_PHASE (every 1 second with beep)
        elif sm.state == state_machine.GameState.DEFUSE_PHASE:
            remaining = sm.current_timer
            current_second = int(remaining)
            
            # Beep every second (except during countdown acceleration)
            if current_second != int(last_beep_time) and remaining >= 10:
                hw.beep(100)
                screen_blink_state = not screen_blink_state
                last_beep_time = remaining
        
        # Generic countdown buzzer (both PLANT and DEFUSE phases)
        if sm.state in [state_machine.GameState.PLANT_PHASE, state_machine.GameState.DEFUSE_PHASE]:
            remaining = sm.current_timer
            
            # Every 0.5s from 10s to 3s
            if 3 < remaining <= 10:
                time_in_half_seconds = int(remaining * 2)  # Convert to 0.5s intervals
                last_time_in_half_seconds = int(last_beep_time * 2)
                if time_in_half_seconds != last_time_in_half_seconds:
                    hw.beep(100)
                    if sm.state == state_machine.GameState.DEFUSE_PHASE:
                        screen_blink_state = not screen_blink_state
                    last_beep_time = remaining
            
            # Every 0.25s from 3s to 0s
            elif 0 < remaining <= 3:
                time_in_quarter_seconds = int(remaining * 4)  # Convert to 0.25s intervals
                last_time_in_quarter_seconds = int(last_beep_time * 4)
                if time_in_quarter_seconds != last_time_in_quarter_seconds:
                    hw.beep(100)
                    if sm.state == state_machine.GameState.DEFUSE_PHASE:
                        screen_blink_state = not screen_blink_state
                    last_beep_time = remaining
        
        # Text blink for end states (every 0.5 seconds)
        if sm.state in [state_machine.GameState.EXPLODED, state_machine.GameState.DEFUSED, state_machine.GameState.TIME_OUT]:
            if blink_timer >= 0.5:
                text_blink_state = not text_blink_state
                blink_timer = 0
        else:
            text_blink_state = False
        
        # Reset blink states when leaving countdown phases
        if sm.state not in [state_machine.GameState.PLANT_PHASE, state_machine.GameState.DEFUSE_PHASE]:
            screen_blink_state = False
        
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
            
            if sm.state == state_machine.GameState.BOOT:
                # # key skips boot video
                if key == '#':
                    sm.transition_to(state_machine.GameState.PIN_TYPE_SELECT)
                    input_buffer = ""
                    # Reset timers
                    blink_timer = 0
                    last_beep_time = -999
                    last_30s_mark = -1
                    # Skip video playback
                    video_ended = True
            
            elif sm.state == state_machine.GameState.PIN_TYPE_SELECT:
                if key in ['1', '2', '3']:
                    input_buffer = key
                elif key == '#':
                    if input_buffer == '1':
                        sm.pin_mode = 1
                        sm.transition_to(state_machine.GameState.CONFIG)
                        config_step = 0
                    elif input_buffer in ['2', '3']:
                        sm.pin_mode = int(input_buffer)
                        sm.transition_to(state_machine.GameState.PLAYER_REGISTRATION)
                        sm.player_phones = []
                        player_step = 1
                    input_buffer = ""
                elif key == '*':
                    input_buffer = ""

            elif sm.state == state_machine.GameState.PLAYER_REGISTRATION:
                if key.isdigit():
                    input_buffer += key
                elif key == '#':
                    if input_buffer:
                        sm.player_phones.append(input_buffer)
                        player_step += 1
                        input_buffer = ""
                    else:
                        message_overlay = "INPUT PHONE"
                        message_timer = 1.0
                elif key == '*':
                    # Request says: press * to enter config that exists today
                    sm.transition_to(state_machine.GameState.CONFIG)
                    config_step =  0
                    input_buffer = ""
            
            elif sm.state == state_machine.GameState.CONFIG:
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
                        input_buffer = "" # Clear for next step per request
                    elif config_step == 1: # Defuse Time
                        sm.defuse_time = val
                        config_step = 2
                        input_buffer = "" # Clear for next step per request
                    else: # Config Done / Ready
                        # Just confirm and go
                        sm.transition_to(state_machine.GameState.READY)
                        config_step = 0
                        input_buffer = ""
                        # Reset timers
                        blink_timer = 0
                        last_beep_time = -999
                        last_30s_mark = -1
            
            elif sm.state == state_machine.GameState.READY:
                if key == '*':
                    sm.transition_to(state_machine.GameState.PLANT_PHASE)
                    input_buffer = ""
                    showing_input = False
                    # Reset timers
                    blink_timer = 0
                    last_beep_time = -999
                    last_30s_mark = -1
            
            elif sm.state == state_machine.GameState.PLANT_PHASE:
                # "To arm ... press *, screen ask for arm pin"
                if not showing_input:
                    if key == '*':
                        showing_input = True
                        input_buffer = ""
                else: 
                    # Showing Input for Arming
                    if key.isdigit():
                         if len(input_buffer) < 4:
                            input_buffer += key
                    elif key == '#': # User must press # to confirm
                        # Check PIN
                        correct_pin = config.ARM_PIN if sm.pin_mode == 1 else sm.dynamic_pin
                        
                        # In dynamic mode, user SETS the pin when planting?
                        # Re-reading prompt: "If the game is in dynamic pin, on plant phase, 
                        # user will press * and define a 4 digit pin, show this set on console please."
                        
                        if sm.pin_mode in [2, 3]:
                            if len(input_buffer) == 4:
                                sm.dynamic_pin = input_buffer
                                print(f"[DYNAMIC PIN] SET TO: {sm.dynamic_pin}")
                                
                                # Mode 3: Send Telegram on Plant
                                if sm.pin_mode == 3:
                                    from bomb_app.telegram_service import telegram_service
                                    msg_counterterrorists = f"THE BOMB HAS BEEN PLANTED!\n{sm.defuse_time} TO EXPLOSION"
                                    telegram_service.send_message(tg_chat_id_counterterrorists, msg_counterterrorists)
                                    msg_terrorists = "BOMB PLANTED!\nPROTECT AT ALL COSTS!"
                                    telegram_service.send_message(tg_chat_id_terrorists, msg_terrorists)
                                
                                sm.transition_to(state_machine.GameState.DEFUSE_PHASE)
                                showing_input = False
                                input_buffer = ""
                                blink_timer = 0
                                last_beep_time = -999
                                last_30s_mark = -1
                            else:
                                message_overlay = "4 DIGITS REQ"
                                message_timer = 2.0
                                input_buffer = ""
                                showing_input = False
                        else:
                            # Static mode
                            if input_buffer == config.ARM_PIN:
                                sm.transition_to(state_machine.GameState.DEFUSE_PHASE)
                                showing_input = False
                                input_buffer = ""
                                blink_timer = 0
                                last_beep_time = -999
                                last_30s_mark = -1
                            else:
                                message_overlay = "WRONG CODE"
                                message_timer = 2.0
                                input_buffer = ""
                                showing_input = False

                    elif key == '*': # Cancel input?
                        showing_input = False
                        input_buffer = ""

            elif sm.state == state_machine.GameState.DEFUSE_PHASE:
                # "To defuse ... press *, screen ask for pin"
                if not showing_input:
                    if key == '*':
                        showing_input = True
                        input_buffer = ""
                        if sm.pin_mode in [2, 3]:
                            defuse_step = 0 # Ask for Phone
                        else:
                            defuse_step = 1 # Ask for PIN directly
                else:
                    if key.isdigit():
                        input_buffer += key
                    elif key == '#': # Confirm
                        if sm.pin_mode in [2, 3]:
                            if defuse_step == 0:
                                # stage: Ask for Phone
                                if input_buffer in sm.player_phones:
                                    sm.log("SYSTEM BREACH DETECTED")
                                    sm.log("BYPASSING ENCRYPTION...")
                                    sm.log("EXPLOITING BUFFER OVERFLOW...")
                                    sm.log("EXTRACTING MASTER PIN...")
                                    sm.log(f"PIN REVEALED: {sm.dynamic_pin}")
                                    
                                    # Show overlay like a "software glitch"
                                    sm.show_console = True
                                    
                                    # Mode 3: Send Telegram on Reveal
                                    if sm.pin_mode == 3:
                                        from bomb_app.telegram_service import telegram_service
                                        msg_counterterrorists = f"PIN FOR DEFUSE: {sm.dynamic_pin}"
                                        telegram_service.send_message(tg_chat_id_counterterrorists, msg_counterterrorists)
                                        msg_terrorists = "DEFUSE IN PROGRESS..."
                                        telegram_service.send_message(tg_chat_id_terrorists, msg_terrorists)
                                        
                                    message_overlay = "PHONE OK"
                                    message_timer = 1.0
                                    input_buffer = ""
                                    defuse_step = 1 # Now ask for PIN
                                else:
                                    message_overlay = "WRONG PHONE"
                                    message_timer = 2.0
                                    input_buffer = ""
                                    showing_input = False
                            else:
                                # stage: Ask for PIN
                                if input_buffer == sm.dynamic_pin:
                                    sm.transition_to(state_machine.GameState.DEFUSED)
                                    blink_timer = 0
                                    last_beep_time = -999
                                    showing_input = False
                                    input_buffer = ""
                                else:
                                    message_overlay = "WRONG CODE"
                                    message_timer = 2.0
                                    input_buffer = ""
                                    showing_input = False
                        else:
                            # Static mode
                            if input_buffer == config.DEFUSE_PIN:
                                sm.transition_to(state_machine.GameState.DEFUSED)
                                blink_timer = 0
                                last_beep_time = -999
                                showing_input = False
                                input_buffer = ""
                            else:
                                message_overlay = "WRONG CODE"
                                message_timer = 2.0
                                input_buffer = ""
                                showing_input = False
                            
                    elif key == '*': # Cancel
                        showing_input = False
                        input_buffer = ""
                        
            elif sm.state in [state_machine.GameState.EXPLODED, state_machine.GameState.DEFUSED, state_machine.GameState.TIME_OUT]:
                if key == '#':
                    # Short press -> Ready
                    sm.transition_to(state_machine.GameState.READY)
                    # Reset timers
                    blink_timer = 0
                    last_beep_time = -999
                    last_30s_mark = -1

        # --- RENDER ---
        display_input = ""
        
        if sm.state == state_machine.GameState.PIN_TYPE_SELECT:
             current_label = "SELECT PIN TYPE (1:STAT, 2:DYN, 3:TG)"
             display_input = input_buffer
        elif sm.state == state_machine.GameState.PLAYER_REGISTRATION:
             current_label = f"PLAYER {player_step} PHONE"
             display_input = input_buffer
        elif sm.state == state_machine.GameState.CONFIG:
             # Determine Context Label
             if config_step == 0:
                 current_label = "SET PLANT TIME"
             elif config_step == 1:
                 current_label = "SET DEFUSE TIME"
             elif config_step == 2:
                 current_label = "CONFIG DONE"
             display_input = input_buffer
        elif sm.state == state_machine.GameState.DEFUSE_PHASE:
             if not showing_input:
                  if sm.pin_mode in [2, 3]:
                       current_label = "PRESS * TO PUT PHONE"
                  else:
                       current_label = "PRESS * TO ENTER PIN"
             else:
                  if sm.pin_mode in [2, 3]:
                       if defuse_step == 0:
                            current_label = "PRESS # IN THE END"
                            display_input = input_buffer
                       else:
                            # Masking for PIN
                            display_val = input_buffer
                            mask_count = 4 - len(display_val)
                            if mask_count < 0: mask_count = 0
                            display_input = display_val + ('*' * mask_count)
                            current_label = "INSERT PIN"
                  else:
                       # Static mode Masking
                       display_val = input_buffer
                       mask_count = 4 - len(display_val)
                       if mask_count < 0: mask_count = 0
                       display_input = display_val + ('*' * mask_count)
                       current_label = "CODE"
        elif sm.state == state_machine.GameState.PLANT_PHASE:
             if showing_input:
                  display_val = input_buffer
                  mask_count = 4 - len(display_val)
                  if mask_count < 0: mask_count = 0
                  display_input = display_val + ('*' * mask_count)
                  current_label = "CODE"
             else:
                  current_label = ""
        else:
             current_label = "" # Unused

        # Get current video frame for BOOT state
        current_display_frame = None
        if sm.state == state_machine.GameState.BOOT:
            if video_ended and video_last_frame is not None:
                # Show frozen last frame
                current_display_frame = video_last_frame
            elif boot_video is not None and not video_ended:
                # Show current frame
                current_display_frame = get_video_frame(boot_video, current_video_frame)

        # Pass input, blink states, and video frame to renderer
        renderer.render(sm, display_input, input_label=current_label, screen_blink=screen_blink_state, text_blink=text_blink_state, video_frame=current_display_frame)
        
        if message_overlay:
            renderer.draw_text(message_overlay, renderer.font_large, config.COLOR_RED, (renderer.width//2, renderer.height//2))
            
        # Removed manual drawing of step_name as it is now in the input label

        renderer.update()

    hw.cleanup()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
