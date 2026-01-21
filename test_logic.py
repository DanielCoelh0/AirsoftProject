
import unittest
from bomb_app.state_machine import StateMachine, GameState

class TestStateMachine(unittest.TestCase):
    def test_flow(self):
        sm = StateMachine()
        sm.set_times(60, 60)
        
        # Initial State
        self.assertEqual(sm.state, GameState.CONFIG)
        
        # Determine transition manually (as Main does)
        sm.transition_to(GameState.READY)
        self.assertEqual(sm.state, GameState.READY)
        
        # Start Plant Phase
        sm.transition_to(GameState.PLANT_PHASE)
        self.assertEqual(sm.state, GameState.PLANT_PHASE)
        self.assertEqual(sm.current_timer, 60)
        
        # Tick timer
        sm.tick(1.0)
        self.assertEqual(sm.current_timer, 59)
        
        # Arming (Simulated)
        sm.transition_to(GameState.DEFUSE_PHASE)
        self.assertEqual(sm.state, GameState.DEFUSE_PHASE)
        self.assertEqual(sm.current_timer, 60) # Should reset to defuse time
        
        # Explode
        sm.current_timer = 1
        sm.tick(1.5)
        self.assertEqual(sm.state, GameState.EXPLODED)

if __name__ == '__main__':
    unittest.main()
