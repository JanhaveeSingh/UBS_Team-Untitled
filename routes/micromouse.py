"""
Micromouse Controller - Spec-compliant implementation
Implements the micromouse movement specification exactly as defined.
"""

import logging
import traceback
import math
from collections import deque
from typing import Dict, List, Tuple, Optional, Any
from flask import request, jsonify

from routes import app

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MicromouseController:
    """Micromouse game state manager and controller (full spec compliance)"""

    def __init__(self):
        self.games: Dict[str, Dict[str, Any]] = {}

        # Valid movement tokens per spec
        self.valid_tokens = {
            # Longitudinal
            'F0', 'F1', 'F2', 'V0', 'V1', 'V2', 'BB',
            # In-place rotations
            'L', 'R',
            # Moving rotations
            'F0L', 'F0R', 'F1L', 'F1R', 'F2L', 'F2R',
            'V0L', 'V0R', 'V1L', 'V1R', 'V2L', 'V2R',
            'BBL', 'BBR',
            # Corner turns (cardinal directions only)
            'F0LT', 'F0RT', 'F0LW', 'F0RW',
            'F1LT', 'F1RT', 'F1LW', 'F1RW', 
            'F2LT', 'F2RT', 'F2LW', 'F2RW',
            'V0LT', 'V0RT', 'V0LW', 'V0RW',
            'V1LT', 'V1RT', 'V1LW', 'V1RW',
            'V2LT', 'V2RT', 'V2LW', 'V2RW'
        }

        # Movement base times per spec
        self.base_times = {
            'in_place_turn': 200,
            'default_action': 200,
            'half_step_cardinal': 500,
            'half_step_intercardinal': 600,
            'corner_tight': 700,
            'corner_wide': 1400
        }

        # Momentum reduction table per spec
        self.momentum_reduction = {
            0.0: 0.00,
            0.5: 0.10,
            1.0: 0.20,
            1.5: 0.275,
            2.0: 0.35,
            2.5: 0.40,
            3.0: 0.45,
            3.5: 0.475,
            4.0: 0.50
        }

        # Constants per spec
        self.GRID_SIZE = 16
        self.GOAL_CELLS = [(7, 7), (7, 8), (8, 7), (8, 8)]  # 2x2 center goal
        self.START_CELL = (0, 0)
        self.TIME_BUDGET = 300_000  # 300 seconds
        self.THINKING_TIME_MS = 50

    def start_new_game(self, game_uuid: str, **kwargs):
        """Initialize a new micromouse game with spec-compliant defaults"""
        self.games[game_uuid] = {
            # Core state from API spec
            'sensor_data': kwargs.get('sensor_data', [0, 0, 0, 0, 0]),
            'total_time_ms': kwargs.get('total_time_ms', 0),
            'goal_reached': kwargs.get('goal_reached', False),
            'best_time_ms': kwargs.get('best_time_ms'),
            'run_time_ms': kwargs.get('run_time_ms', 0),
            'run': kwargs.get('run', 0),
            'momentum': kwargs.get('momentum', 0),
            'orientation': kwargs.get('orientation', 0),  # 0° = North per spec
            'position': kwargs.get('position', (0, 0)),  # For internal tracking
            
            # Internal state for pathfinding and exploration
            'maze_knowledge': {},  # Track discovered walls/passages
            'exploration_strategy': 'wall_follow',  # Simple strategy
            'recent_moves': deque(maxlen=10),  # For loop detection
            'stuck_counter': 0,
            'last_position': (0, 0),
            'position_history': deque(maxlen=5)
        }
        logger.info(f"Started new game {game_uuid}")

    def get_next_instructions(self, game_uuid: str) -> Tuple[List[str], bool]:
        """Generate next movement instructions per spec"""
        if game_uuid not in self.games:
            return [], True
            
        game = self.games[game_uuid]
        
        # Check end conditions per spec
        if (game['total_time_ms'] >= self.TIME_BUDGET or 
            game['run'] >= 10):  # Reasonable run limit
            return [], True
        
        try:
            instructions = self._generate_instructions(game)
            return instructions, False
        except Exception as e:
            logger.info(f"Error generating instructions: {e}")
            logger.info(traceback.format_exc())
            # Safe fallback - brake to avoid crash
            return ['BB'], False

    def _generate_instructions(self, game: Dict[str, Any]) -> List[str]:
        """Generate movement instructions based on current state"""
        momentum = game['momentum']
        sensors = game['sensor_data'][:5]  # Ensure 5 sensors
        orientation = game['orientation']
        position = game['position']
        
        logger.info(f"Current state - Position: {position}, Orientation: {orientation}°, Momentum: {momentum}, Sensors: {sensors}")
        
        # Safety first - if we have momentum and front wall, brake
        if momentum > 0 and len(sensors) > 2 and sensors[2] == 1:  # Front sensor detects wall
            logger.info("Front wall detected with forward momentum, braking")
            return ['BB']
        
        # If at goal with momentum, brake to complete
        if self._is_in_goal_area(position) and momentum != 0:
            logger.info("In goal area, braking to complete")
            return ['BB']
        
        # If at goal and stopped, we're done
        if self._is_in_goal_area(position) and momentum == 0:
            logger.info("Goal reached and stopped!")
            return []
        
        # Detect if stuck in loop
        if self._is_stuck_in_loop(game):
            return self._escape_loop(game)
        
        # Simple but effective strategy: wall following with goal seeking
        return self._wall_follow_strategy(game)

    def _wall_follow_strategy(self, game: Dict[str, Any]) -> List[str]:
        """Implement simplified wall following strategy"""
        momentum = game['momentum']
        sensors = game['sensor_data'][:5] if len(game['sensor_data']) >= 5 else [0, 0, 0, 0, 0]
        
        # If we have momentum, need to brake first for full control
        if momentum > 0:
            logger.info("Braking to stop before making decision")
            return ['BB']
        
        # Simple wall following: prefer right, then forward, then left, then back
        # sensors: [left, left-front, front, right-front, right]
        
        # Priority 1: Turn right if no right wall and no right-front wall
        if len(sensors) >= 5 and sensors[4] == 0 and sensors[3] == 0:
            logger.info("Right side clear, turning right and moving")
            return ['R', 'F1']
        
        # Priority 2: Go forward if no front wall
        if len(sensors) >= 3 and sensors[2] == 0:
            logger.info("Front clear, moving forward")
            return ['F1']
        
        # Priority 3: Turn left if no left wall
        if len(sensors) >= 1 and sensors[0] == 0:
            logger.info("Left side clear, turning left and moving")
            return ['L', 'F1']
        
        # Priority 4: Turn around (all sides blocked)
        logger.info("All sides blocked, turning around")
        return ['R', 'R']

    def _is_stuck_in_loop(self, game: Dict[str, Any]) -> bool:
        """Detect if mouse is stuck in a repetitive pattern"""
        position = game['position']
        history = game['position_history']
        
        # Add current position to history
        history.append(position)
        
        # Check if we've been in the same area too long
        if len(history) >= 4:
            recent_positions = list(history)[-4:]
            if len(set(recent_positions)) <= 2:  # Only visiting 1-2 positions
                game['stuck_counter'] += 1
                return game['stuck_counter'] >= 3
        
        return False

    def _escape_loop(self, game: Dict[str, Any]) -> List[str]:
        """Escape from detected loop"""
        logger.info("Loop detected, attempting escape")
        game['stuck_counter'] = 0  # Reset counter
        
        # Try different escape strategies
        sensors = game['sensor_data'][:5]
        
        # Strategy 1: Force left turn if possible
        if sensors[0] == 0:  # Left clear
            return ['L', 'F2']
        
        # Strategy 2: Force right turn if possible  
        if sensors[4] == 0:  # Right clear
            return ['R', 'F2']
        
        # Strategy 3: Move forward if clear
        if sensors[2] == 0:  # Front clear
            return ['F2']
        
        # Last resort: turn around
        return ['R', 'R']

    def _is_in_goal_area(self, position: Tuple[int, int]) -> bool:
        """Check if position is in the 2x2 goal area"""
        x, y = position
        return (x, y) in self.GOAL_CELLS

    def update_game_state(self, game_uuid: str, new_state: Dict[str, Any]):
        """Update game state from API payload"""
        if game_uuid not in self.games:
            logger.info(f"Update for unknown game {game_uuid}")
            return
            
        game = self.games[game_uuid]
        
        # Update fields from API spec
        for field in ['sensor_data', 'total_time_ms', 'goal_reached', 
                     'best_time_ms', 'run_time_ms', 'run', 'momentum', 'orientation']:
            if field in new_state:
                game[field] = new_state[field]
        
        # Handle position update
        if 'position' in new_state:
            pos = new_state['position']
            if isinstance(pos, (list, tuple)) and len(pos) == 2:
                game['position'] = tuple(pos)
        
        # Ensure sensor_data is always 5 elements
        if 'sensor_data' in new_state:
            sensors = new_state['sensor_data'] or [0, 0, 0, 0, 0]
            game['sensor_data'] = (list(sensors)[:5] + [0]*5)[:5]
        
        # Update position history for loop detection
        if 'position' in game:
            game['position_history'].append(game['position'])
        
        # Check if we completed the goal
        if (self._is_in_goal_area(game['position']) and 
            game['momentum'] == 0 and 
            not game['goal_reached']):
            
            game['goal_reached'] = True
            if (game['best_time_ms'] is None or 
                game['run_time_ms'] < game['best_time_ms']):
                game['best_time_ms'] = game['run_time_ms']
            logger.info(f"Goal reached! Run time: {game['run_time_ms']}ms")

# Global controller instance
controller = MicromouseController()

@app.route('/micro-mouse', methods=['POST'])
def micromouse():
    """Main micromouse endpoint per API specification"""
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({'error': 'Empty request body'}), 400
            
        game_uuid = payload.get('game_uuid')
        if not game_uuid:
            return jsonify({'error': 'Missing game_uuid'}), 400

        # Initialize or update game
        if game_uuid not in controller.games:
            logger.info(f"Starting new game {game_uuid}")
            # Remove game_uuid from payload to avoid duplicate argument
            init_payload = {k: v for k, v in payload.items() if k != 'game_uuid'}
            controller.start_new_game(game_uuid, **init_payload)
        else:
            logger.info(f"Updating game {game_uuid}")
            controller.update_game_state(game_uuid, payload)

        # Generate instructions
        instructions, end_flag = controller.get_next_instructions(game_uuid)
        
        response = {
            'instructions': instructions,
            'end': end_flag
        }
        
        logger.info(f"Game {game_uuid} -> {response}")
        return jsonify(response)
        
    except Exception as e:
        logger.info(f"Error in micromouse endpoint: {e}")
        logger.info(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/micro-mouse/stats/<game_uuid>', methods=['GET'])
def get_micromouse_stats(game_uuid):
    """Get game statistics"""
    try:
        if game_uuid not in controller.games:
            return jsonify({'error': 'Game not found'}), 404
            
        game = controller.games[game_uuid]
        stats = {
            'game_uuid': game_uuid,
            'position': game['position'],
            'orientation': game['orientation'],
            'momentum': game['momentum'],
            'run': game['run'],
            'run_time_ms': game['run_time_ms'],
            'best_time_ms': game['best_time_ms'],
            'goal_reached': game['goal_reached'],
            'total_time_ms': game['total_time_ms'],
            'time_remaining': controller.TIME_BUDGET - game['total_time_ms']
        }
        return jsonify(stats)
        
    except Exception as e:
        logger.info(f"Error getting stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/micro-mouse/debug/<game_uuid>', methods=['GET'])
def get_micromouse_debug(game_uuid):
    """Get debug information"""
    try:
        if game_uuid not in controller.games:
            return jsonify({'error': 'Game not found'}), 404
            
        game = controller.games[game_uuid]
        debug_info = {
            'game_uuid': game_uuid,
            'position': game['position'],
            'orientation': game['orientation'],
            'momentum': game['momentum'],
            'sensor_data': game['sensor_data'],
            'run': game['run'],
            'goal_reached': game['goal_reached'],
            'stuck_counter': game.get('stuck_counter', 0),
            'exploration_strategy': game.get('exploration_strategy', 'unknown'),
            'recent_moves': list(game.get('recent_moves', [])),
            'position_history': list(game.get('position_history', []))
        }
        return jsonify(debug_info)
        
    except Exception as e:
        logger.info(f"Error getting debug info: {e}")
        return jsonify({'error': 'Internal server error'}), 500
