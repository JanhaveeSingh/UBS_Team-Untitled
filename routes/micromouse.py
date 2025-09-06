import json
import logging
from flask import request
from routes import app

logger = logging.getLogger(__name__)

class SimpleMicroMouse:
    def __init__(self):
        self.game_uuid = None
        self.last_sensor_data = None
        self.stuck_count = 0
        self.turn_preference = 'R'  # Start with right preference
        
    def reset_for_new_game(self, game_uuid):
        if self.game_uuid != game_uuid:
            self.game_uuid = game_uuid
            self.last_sensor_data = None
            self.stuck_count = 0
            self.turn_preference = 'R'
            logger.info(f"Reset for new game: {game_uuid}")
    
    def is_stuck(self, sensor_data):
        """Check if we're getting the same sensor readings repeatedly"""
        if self.last_sensor_data == sensor_data:
            self.stuck_count += 1
        else:
            self.stuck_count = 0
            self.last_sensor_data = sensor_data
        return self.stuck_count > 3
    
    def solve(self, game_data):
        """Ultra-simple wall-following logic"""
        momentum = game_data['momentum']
        sensor_data = game_data['sensor_data']
        goal_reached = game_data['goal_reached']
        
        logger.info(f"Momentum: {momentum}, Sensors: {sensor_data}")
        
        # If goal reached, stop
        if goal_reached:
            logger.info("Goal reached!")
            return []
        
        # If we have momentum
        if momentum > 0:
            front_sensor = sensor_data[2]  # Front sensor
            if front_sensor == 1:  # Wall directly ahead
                logger.info("Wall ahead, braking")
                return ['BB']
            else:
                logger.info("Path clear, continuing")
                return ['F1']
        elif momentum < 0:
            logger.info("Moving backward, braking")
            return ['BB']
        
        # At rest (momentum = 0) - decide next move
        front = sensor_data[2]    # 0°
        left = sensor_data[1]     # -45°
        right = sensor_data[3]    # +45°
        
        # Check if we're stuck in a loop
        if self.is_stuck(sensor_data):
            logger.info("Stuck detected, switching turn preference")
            self.turn_preference = 'L' if self.turn_preference == 'R' else 'R'
            self.stuck_count = 0
        
        # Simple priority: forward > preferred_turn > other_turn
        if front == 0:  # Front is clear
            logger.info("Moving forward")
            return ['F2']
        elif self.turn_preference == 'R' and right == 0:  # Right is clear and preferred
            logger.info("Turning right")
            return ['R']
        elif self.turn_preference == 'L' and left == 0:  # Left is clear and preferred
            logger.info("Turning left")
            return ['L']
        elif right == 0:  # Right is clear (fallback)
            logger.info("Turning right (fallback)")
            return ['R']
        elif left == 0:  # Left is clear (fallback)
            logger.info("Turning left (fallback)")
            return ['L']
        else:  # All directions blocked, turn around
            logger.info("All blocked, turning around")
            return ['R', 'R', 'R', 'R']  # 180 degree turn

# Global solver
solver = SimpleMicroMouse()

@app.route('/micro-mouse', methods=['POST'])
def micromouse():
    try:
        data = request.get_json()
        logger.info("Micromouse request: {}".format(data))
        
        # Reset for new games
        game_uuid = data.get('game_uuid')
        solver.reset_for_new_game(game_uuid)
        
        # Get instructions
        instructions = solver.solve(data)
        
        result = {
            "instructions": instructions,
            "end": False
        }
        
        logger.info("Response: {}".format(result))
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return json.dumps({
            "instructions": [],
            "end": False
        })
