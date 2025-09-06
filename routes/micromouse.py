import json
import logging
from flask import request
from routes import app
from collections import deque, defaultdict
import heapq
from typing import List, Tuple, Optional, Dict, Set

logger = logging.getLogger(__name__)

# Global solver instance to maintain state across requests
class MicroMouseSolver:
    def __init__(self):
        # Maze representation (16x16 grid)
        self.maze_size = 16
        self.walls = set()  # Set of wall coordinates
        self.visited_cells = set()  # Cells we've visited
        
        # Goal location (center 2x2)
        self.goal_cells = {(7, 7), (7, 8), (8, 7), (8, 8)}
        
        # Mouse state - DON'T track position ourselves, let the game do it
        self.facing_direction = 0  # 0=North, 2=East, 4=South, 6=West (cardinal only)
        
        # Exploration strategy
        self.exploration_complete = False
        self.game_uuid = None
        
        # Simple movement strategy
        self.last_sensor_data = None
        self.movement_history = []
        
    def reset_for_new_game(self, game_uuid):
        """Reset solver state for a new game"""
        if self.game_uuid != game_uuid:
            self.game_uuid = game_uuid
            self.walls = set()
            self.visited_cells = set()
            self.facing_direction = 0  # Start facing North
            self.exploration_complete = False
            self.last_sensor_data = None
            self.movement_history = []
            logger.info(f"Reset solver for new game: {game_uuid}")
    
    def can_move_forward(self, sensor_data) -> bool:
        """Check if we can move forward based on front sensor (index 2)"""
        return sensor_data[2] == 0  # 0 means no wall, 1 means wall
    
    def can_turn_left(self, sensor_data) -> bool:
        """Check if we can turn left and then move (sensor index 1 = -45°, index 0 = -90°)"""
        return sensor_data[1] == 0 or sensor_data[0] == 0
    
    def can_turn_right(self, sensor_data) -> bool:
        """Check if we can turn right and then move (sensor index 3 = +45°, index 4 = +90°)"""
        return sensor_data[3] == 0 or sensor_data[4] == 0
    
    def is_dead_end(self, sensor_data) -> bool:
        """Check if we're in a dead end (walls on front, left, and right)"""
        front_blocked = sensor_data[2] == 1
        left_blocked = sensor_data[1] == 1 and sensor_data[0] == 1
        right_blocked = sensor_data[3] == 1 and sensor_data[4] == 1
        return front_blocked and left_blocked and right_blocked
    
    def wall_follow_strategy(self, sensor_data, momentum) -> List[str]:
        """Simple wall-following strategy (right-hand rule)"""
        instructions = []
        
        # If we have momentum, we need to handle it carefully
        if momentum != 0:
            # If we're moving and there's a wall ahead, brake
            if sensor_data[2] == 1:  # Wall in front
                return ['BB']  # Brake
            else:
                # Continue moving if path is clear
                return ['F1']
        
        # At rest (momentum = 0), we can turn or accelerate
        # Right-hand wall following: try right, then forward, then left, then back
        
        # First, try to turn right and move
        if self.can_turn_right(sensor_data):
            instructions.append('R')  # Turn right 45 degrees
            # Need another turn to face cardinal direction if needed
            if len(instructions) == 1:  # Only turned once, might need to align
                instructions.append('R')  # Turn right again to face cardinal
            return instructions
        
        # If can't go right, try forward
        elif self.can_move_forward(sensor_data):
            return ['F2']  # Accelerate forward
        
        # If can't go forward, try left
        elif self.can_turn_left(sensor_data):
            instructions.append('L')  # Turn left 45 degrees
            if len(instructions) == 1:  # Only turned once
                instructions.append('L')  # Turn left again
            return instructions
        
        # If all else fails, turn around (4 right turns = 180 degrees)
        else:
            return ['R', 'R', 'R', 'R']  # Turn around
    
    def simple_exploration_strategy(self, sensor_data, momentum) -> List[str]:
        """Very simple exploration: prefer forward, then right, then left, then back"""
        
        # If we have momentum, handle it
        if momentum > 0:
            if sensor_data[2] == 1:  # Wall ahead, need to brake
                return ['BB']
            else:
                return ['F1']  # Keep moving forward
        elif momentum < 0:
            return ['BB']  # Brake if moving backward
        
        # At rest, decide where to go
        # Priority: forward > right > left > back
        if sensor_data[2] == 0:  # Can go forward
            return ['F2']
        elif sensor_data[3] == 0 or sensor_data[4] == 0:  # Can go right
            return ['R']  # Turn right once (45 degrees)
        elif sensor_data[1] == 0 or sensor_data[0] == 0:  # Can go left  
            return ['L']  # Turn left once (45 degrees)
        else:
            # Turn around - do it in steps to avoid crashing
            return ['R', 'R']  # Turn 90 degrees right
    
    def generate_instructions(self, game_data: dict) -> List[str]:
        """Main logic to generate movement instructions"""
        sensor_data = game_data['sensor_data']
        momentum = game_data['momentum']
        goal_reached = game_data['goal_reached']
        total_time = game_data['total_time_ms']
        
        logger.info(f"Momentum: {momentum}, Sensor data: {sensor_data}")
        
        # If we've reached the goal, stop
        if goal_reached:
            logger.info("Goal reached! Stopping.")
            return ['BB'] if momentum != 0 else []
        
        # If we're running out of time, try to end gracefully
        if total_time > 280000:  # 280 seconds, leave 20 seconds buffer
            logger.info("Time running out, ending challenge")
            return []
        
        # Use simple exploration strategy
        try:
            instructions = self.simple_exploration_strategy(sensor_data, momentum)
            logger.info(f"Generated instructions: {instructions}")
            return instructions
        except Exception as e:
            logger.error(f"Error generating instructions: {e}")
            # Safe fallback: brake if moving, otherwise do nothing
            return ['BB'] if momentum != 0 else []

# Global solver instance
solver = MicroMouseSolver()

@app.route('/micro-mouse', methods=['POST'])
def micromouse():
    try:
        data = request.get_json()
        logger.info("Micromouse data received: {}".format(data))
        
        # Reset solver for new games
        game_uuid = data.get('game_uuid')
        solver.reset_for_new_game(game_uuid)
        
        # Generate instructions
        instructions = solver.generate_instructions(data)
        
        result = {
            "instructions": instructions,
            "end": False
        }
        
        logger.info("Micromouse result: {}".format(result))
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Error in micromouse route: {str(e)}")
        # Return safe fallback response
        return json.dumps({
            "instructions": ["BB"],
            "end": False
        })
