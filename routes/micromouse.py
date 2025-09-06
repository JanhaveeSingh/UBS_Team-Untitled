"""
Micromouse Controller Implementation
Implements the micromouse maze navigation system according to the specification.
"""

import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from collections import deque
import math
from flask import request, jsonify

from routes import app

logger = logging.getLogger(__name__)

class MicromouseController:
    """
    Micromouse game state manager and controller
    """
    
    def __init__(self):
        self.games = {}
        
        # Movement token definitions
        self.valid_tokens = {
            'F0', 'F1', 'F2',  # Forward movements
            'V0', 'V1', 'V2',  # Reverse movements
            'BB',               # Brake
            'L', 'R',           # In-place rotations
            # Moving rotations
            'F0L', 'F0R', 'F1L', 'F1R', 'F2L', 'F2R',
            'V0L', 'V0R', 'V1L', 'V1R', 'V2L', 'V2R',
            'BBL', 'BBR',
            # Corner turns
            'F0LT', 'F0RT', 'F0LW', 'F0RW',
            'F1LT', 'F1RT', 'F1LW', 'F1RW',
            'F2LT', 'F2RT', 'F2LW', 'F2RW',
            'V0LT', 'V0RT', 'V0LW', 'V0RW',
            'V1LT', 'V1RT', 'V1LW', 'V1RW',
            'V2LT', 'V2RT', 'V2LW', 'V2RW',
            # Corner turns with end rotation
            'F0LTL', 'F0LTR', 'F0RTL', 'F0RTR',
            'F0LWL', 'F0LWR', 'F0RWL', 'F0RWR',
            # Add more corner turn combinations as needed
        }
        
        # Base movement times (ms)
        self.base_times = {
            'in_place_turn': 200,
            'default_action': 200,
            'half_step_cardinal': 500,
            'half_step_intercardinal': 600,
            'corner_tight': 700,
            'corner_wide': 1400
        }
        
        # Momentum reduction table
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
        
    def start_new_game(self, game_uuid: str, sensor_data: List[int], 
                      total_time_ms: int = 0, goal_reached: bool = False,
                      best_time_ms: Optional[int] = None, run_time_ms: int = 0,
                      run: int = 0, momentum: int = 0):
        """Initialize a new micromouse game"""
        self.games[game_uuid] = {
            'sensor_data': sensor_data,
            'total_time_ms': total_time_ms,
            'goal_reached': goal_reached,
            'best_time_ms': best_time_ms,
            'run_time_ms': run_time_ms,
            'run': run,
            'momentum': momentum,
            'position': (0, 0),  # Start at bottom-left
            'orientation': 0,  # Facing North (0°)
            'maze_map': {},  # Discovered walls and passages
            'visited_cells': set(),
            'path_to_goal': [],
            'current_run_started': False,
            'time_budget': 300000,  # 300 seconds total
            'thinking_time': 50  # 50ms per request
        }
        logger.info(f"Started new micromouse game {game_uuid}")
        
    def get_next_instructions(self, game_uuid: str) -> Tuple[List[str], bool]:
        """
        Generate next movement instructions for the micromouse
        Returns (instructions, end_flag)
        """
        if game_uuid not in self.games:
            return [], True
            
        game = self.games[game_uuid]
        
        # Check if we should end the challenge
        if (game['total_time_ms'] >= game['time_budget'] or 
            game['goal_reached'] or 
            game['run'] >= 10):  # Max 10 runs
            return [], True
            
        # Check if we need to start a new run
        if not game['current_run_started']:
            game['current_run_started'] = True
            game['run'] += 1
            game['run_time_ms'] = 0
            game['goal_reached'] = False
            game['position'] = (0, 0)
            game['orientation'] = 0
            game['momentum'] = 0
            logger.info(f"Starting run {game['run']} for game {game_uuid}")
        
        # Generate movement strategy
        instructions = self._generate_movement_strategy(game_uuid)
        
        return instructions, False
    
    def _generate_movement_strategy(self, game_uuid: str) -> List[str]:
        """Generate movement instructions based on current state using pathfinding"""
        game = self.games[game_uuid]
        position = game['position']
        orientation = game['orientation']
        momentum = game['momentum']
        sensor_data = game['sensor_data']
        
        # Debug logging
        logger.debug(f"Game {game_uuid}: position={position}, orientation={orientation}, momentum={momentum}")
        logger.debug(f"Position type: {type(position)}, position value: {repr(position)}")
        
        # Ensure position is valid
        if not isinstance(position, tuple) or len(position) != 2:
            logger.error(f"Invalid position in movement strategy: {position}, type: {type(position)}")
            game['position'] = (0, 0)
            position = (0, 0)
        
        # Update maze map with sensor data
        try:
            self._update_maze_map(game, position, orientation, sensor_data)
        except Exception as e:
            logger.error(f"Error updating maze map: {str(e)}")
            return self._exploration_strategy(game)
        
        # Use pathfinding to determine next moves
        try:
            path = self._find_path_to_goal(game)
        except Exception as e:
            logger.error(f"Error in pathfinding: {str(e)}")
            logger.error(f"Pathfinding error type: {type(e)}")
            import traceback
            logger.error(f"Pathfinding traceback: {traceback.format_exc()}")
            return self._exploration_strategy(game)
        
        if not path:
            # No path found, use exploration strategy
            logger.debug("No path found, using exploration strategy")
            return self._exploration_strategy(game)
        
        # Convert path to movement instructions
        try:
            instructions = self._path_to_instructions(game, path)
        except Exception as e:
            logger.error(f"Error converting path to instructions: {str(e)}")
            return self._exploration_strategy(game)
        
        # Validate instructions
        valid_instructions = []
        for instruction in instructions:
            if self._validate_instruction(game, instruction):
                valid_instructions.append(instruction)
            else:
                break  # Stop at first invalid instruction
        
        # Safety check: if we're about to move forward and there's a wall, stop
        if valid_instructions and valid_instructions[0].startswith('F'):
            front_wall = sensor_data[2] if len(sensor_data) > 2 else 0
            if front_wall:
                logger.warning("Safety check: preventing forward movement into wall")
                return ['BB']  # Just brake
                
        return valid_instructions[:5]  # Limit batch size
    
    def _exploration_strategy(self, game: Dict[str, Any]) -> List[str]:
        """Fallback exploration strategy when pathfinding fails"""
        position = game['position']
        orientation = game['orientation']
        momentum = game['momentum']
        sensor_data = game['sensor_data']
        
        # Ensure position is valid
        if not isinstance(position, tuple) or len(position) != 2:
            logger.error(f"Invalid position in exploration strategy: {position}")
            game['position'] = (0, 0)
            position = (0, 0)
        
        instructions = []
        
        # If we're at the start and not moving, begin exploration
        if position == (0, 0) and momentum == 0:
            # Check for walls before starting
            front_wall = sensor_data[2] if len(sensor_data) > 2 else 0
            if front_wall:
                # Wall ahead, turn right first
                instructions = ['R', 'F2']
            else:
                instructions = ['F2', 'F2']
            
        # If we have momentum, continue forward or adjust
        elif momentum > 0:
            # Check sensors for walls
            front_wall = sensor_data[2] if len(sensor_data) > 2 else 0
            left_wall = sensor_data[0] if len(sensor_data) > 0 else 0
            right_wall = sensor_data[4] if len(sensor_data) > 4 else 0
            
            logger.debug(f"Exploration: front_wall={front_wall}, left_wall={left_wall}, right_wall={right_wall}")
            
            if front_wall:
                # Wall ahead, need to turn
                if not left_wall:
                    instructions = ['BB', 'L', 'F2']
                elif not right_wall:
                    instructions = ['BB', 'R', 'F2']
                else:
                    instructions = ['BB', 'L', 'L', 'F2']
            else:
                # No wall ahead, can move forward
                if momentum < 4:
                    instructions = ['F2']
                else:
                    instructions = ['F1']
                    
        elif momentum < 0:
            instructions = ['V0']
        else:
            # No momentum, check for walls before moving
            front_wall = sensor_data[2] if len(sensor_data) > 2 else 0
            left_wall = sensor_data[0] if len(sensor_data) > 0 else 0
            right_wall = sensor_data[4] if len(sensor_data) > 4 else 0
            
            logger.debug(f"Zero momentum: front_wall={front_wall}, left_wall={left_wall}, right_wall={right_wall}")
            
            if front_wall:
                # Wall ahead, need to turn
                if not left_wall:
                    instructions = ['L', 'F2']
                elif not right_wall:
                    instructions = ['R', 'F2']
                else:
                    instructions = ['L', 'L', 'F2']
            else:
                instructions = ['F2']
            
        return instructions
    
    def _update_maze_map(self, game: Dict[str, Any], position: Tuple[int, int], 
                        orientation: int, sensor_data: List[int]):
        """Update the maze map based on sensor readings"""
        # Ensure position is a valid tuple
        if not isinstance(position, tuple) or len(position) != 2:
            logger.error(f"Invalid position in _update_maze_map: {position}")
            return
            
        x, y = position
        
        # Map sensor readings to wall positions
        sensor_angles = [-90, -45, 0, 45, 90]
        
        for i, sensor_value in enumerate(sensor_data):
            if sensor_value > 0:  # Wall detected
                angle = sensor_angles[i] if i < len(sensor_angles) else 0
                wall_pos = self._get_wall_position(x, y, orientation, angle)
                if wall_pos:
                    game['maze_map'][wall_pos] = 'wall'
            else:  # No wall
                angle = sensor_angles[i] if i < len(sensor_angles) else 0
                wall_pos = self._get_wall_position(x, y, orientation, angle)
                if wall_pos:
                    game['maze_map'][wall_pos] = 'passage'
    
    def _get_wall_position(self, x: int, y: int, orientation: int, sensor_angle: int) -> Optional[Tuple[int, int]]:
        """Calculate wall position based on mouse position, orientation, and sensor angle"""
        # Calculate absolute angle
        absolute_angle = (orientation + sensor_angle) % 360
        
        # Convert to direction
        if absolute_angle == 0:  # North
            return (x, y - 1)
        elif absolute_angle == 45:  # Northeast
            return (x + 1, y - 1)
        elif absolute_angle == 90:  # East
            return (x + 1, y)
        elif absolute_angle == 135:  # Southeast
            return (x + 1, y + 1)
        elif absolute_angle == 180:  # South
            return (x, y + 1)
        elif absolute_angle == 225:  # Southwest
            return (x - 1, y + 1)
        elif absolute_angle == 270:  # West
            return (x - 1, y)
        elif absolute_angle == 315:  # Northwest
            return (x - 1, y - 1)
        
        return None
    
    def _find_path_to_goal(self, game: Dict[str, Any]) -> List[Tuple[int, int]]:
        """Find path to goal using A* algorithm"""
        start = game['position']
        goal = (7, 7)  # Center of goal area
        
        # Ensure start is a valid tuple
        if not isinstance(start, tuple) or len(start) != 2:
            logger.error(f"Invalid start position in pathfinding: {start}")
            return []
        
        if start == goal:
            return []
            
        # A* pathfinding
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        
        try:
            f_score = {start: self._heuristic(start, goal)}
        except Exception as e:
            logger.error(f"Error calculating initial heuristic: {str(e)}")
            logger.error(f"Start: {start}, Goal: {goal}")
            return []
        
        while open_set:
            current = min(open_set, key=lambda x: x[0])[1]
            open_set = [item for item in open_set if item[1] != current]
            
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            # Check all neighbors
            try:
                neighbors = self._get_neighbors(current, game['maze_map'])
                for neighbor in neighbors:
                    tentative_g = g_score[current] + 1
                    
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + self._heuristic(neighbor, goal)
                        
                        if not any(item[1] == neighbor for item in open_set):
                            open_set.append((f_score[neighbor], neighbor))
            except Exception as e:
                logger.error(f"Error checking neighbors for {current}: {str(e)}")
                continue
        
        return []  # No path found
    
    def _get_neighbors(self, position: Tuple[int, int], maze_map: Dict) -> List[Tuple[int, int]]:
        """Get valid neighboring positions"""
        # Ensure position is a valid tuple
        if not isinstance(position, tuple) or len(position) != 2:
            logger.error(f"Invalid position in _get_neighbors: {position}")
            return []
            
        x, y = position
        neighbors = []
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < 16 and 0 <= new_y < 16 and 
                (new_x, new_y) not in maze_map or maze_map[(new_x, new_y)] != 'wall'):
                neighbors.append((new_x, new_y))
                
        return neighbors
    
    def _heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Manhattan distance heuristic"""
        try:
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        except (TypeError, IndexError) as e:
            logger.error(f"Error in heuristic calculation: pos1={pos1}, pos2={pos2}, error={e}")
            return 0
    
    def _path_to_instructions(self, game: Dict[str, Any], path: List[Tuple[int, int]]) -> List[str]:
        """Convert path to movement instructions"""
        if not path:
            return []
            
        current_pos = game['position']
        current_orientation = game['orientation']
        current_momentum = game['momentum']
        instructions = []
        
        # Ensure current_pos is a valid tuple
        if not isinstance(current_pos, tuple) or len(current_pos) != 2:
            logger.error(f"Invalid current_pos in path_to_instructions: {current_pos}")
            return []
        
        for next_pos in path:
            # Ensure next_pos is a valid tuple
            if not isinstance(next_pos, tuple) or len(next_pos) != 2:
                logger.error(f"Invalid next_pos in path_to_instructions: {next_pos}")
                continue
                
            # Calculate required movement
            dx = next_pos[0] - current_pos[0]
            dy = next_pos[1] - current_pos[1]
            
            # Determine required orientation
            if dx == 1 and dy == 0:  # East
                target_orientation = 90
            elif dx == -1 and dy == 0:  # West
                target_orientation = 270
            elif dx == 0 and dy == 1:  # South
                target_orientation = 180
            elif dx == 0 and dy == -1:  # North
                target_orientation = 0
            else:
                continue  # Skip diagonal moves for now
            
            # Calculate rotation needed
            rotation_needed = (target_orientation - current_orientation) % 360
            
            # Add rotation instructions
            if rotation_needed == 90:
                instructions.append('R')
            elif rotation_needed == 270:
                instructions.append('L')
            elif rotation_needed == 180:
                instructions.extend(['R', 'R'])
            
            # Add forward movement
            if current_momentum == 0:
                instructions.append('F2')
            elif current_momentum < 4:
                instructions.append('F2')
            else:
                instructions.append('F1')
            
            current_pos = next_pos
            current_orientation = target_orientation
            current_momentum = min(4, current_momentum + 1)
        
        return instructions
    
    def _validate_instruction(self, game: Dict[str, Any], instruction: str) -> bool:
        """Validate if an instruction is legal given current game state"""
        if instruction not in self.valid_tokens:
            return False
            
        momentum = game['momentum']
        
        # Check momentum constraints
        if instruction.startswith('F') and momentum < 0:
            return False  # Can't accelerate forward with negative momentum
        if instruction.startswith('V') and momentum > 0:
            return False  # Can't accelerate reverse with positive momentum
            
        # Check in-place rotation constraints
        if instruction in ['L', 'R'] and momentum != 0:
            return False  # Must be at momentum 0 for in-place rotation
            
        # Check moving rotation constraints
        if len(instruction) == 2 and instruction[1] in ['L', 'R']:
            base_token = instruction[0]
            if base_token.startswith('F'):
                m_eff = abs(momentum) / 2  # Simplified calculation
                if m_eff > 1:
                    return False
            elif base_token.startswith('V'):
                m_eff = abs(momentum) / 2
                if m_eff > 1:
                    return False
                    
        return True
    
    def calculate_movement_time(self, instruction: str, momentum_in: int, momentum_out: int) -> int:
        """Calculate movement time based on instruction and momentum"""
        if instruction in ['L', 'R']:
            return self.base_times['in_place_turn']
        
        if instruction == 'BB' and momentum_in == 0:
            return self.base_times['default_action']
        
        # Calculate effective momentum
        m_eff = (abs(momentum_in) + abs(momentum_out)) / 2
        
        # Get base time
        if instruction in ['F0', 'F1', 'F2', 'V0', 'V1', 'V2', 'BB']:
            # Half-step movement
            if self._is_cardinal_direction(instruction):
                base_time = self.base_times['half_step_cardinal']
            else:
                base_time = self.base_times['half_step_intercardinal']
        elif 'T' in instruction:
            base_time = self.base_times['corner_tight']
        elif 'W' in instruction:
            base_time = self.base_times['corner_wide']
        else:
            base_time = self.base_times['default_action']
        
        # Apply momentum reduction
        reduction = self._get_momentum_reduction(m_eff)
        actual_time = base_time * (1 - reduction)
        
        return int(round(actual_time))
    
    def _is_cardinal_direction(self, instruction: str) -> bool:
        """Check if instruction moves in cardinal direction"""
        # Simplified - assumes cardinal for basic movements
        return instruction in ['F0', 'F1', 'F2', 'V0', 'V1', 'V2', 'BB']
    
    def _get_momentum_reduction(self, m_eff: float) -> float:
        """Get momentum reduction percentage for given effective momentum"""
        # Clamp to valid range
        m_eff = max(0.0, min(4.0, m_eff))
        
        # Find the two closest values in the table
        keys = sorted(self.momentum_reduction.keys())
        
        if m_eff <= keys[0]:
            return self.momentum_reduction[keys[0]]
        if m_eff >= keys[-1]:
            return self.momentum_reduction[keys[-1]]
        
        # Linear interpolation
        for i in range(len(keys) - 1):
            if keys[i] <= m_eff <= keys[i + 1]:
                x1, y1 = keys[i], self.momentum_reduction[keys[i]]
                x2, y2 = keys[i + 1], self.momentum_reduction[keys[i + 1]]
                
                # Linear interpolation
                return y1 + (y2 - y1) * (m_eff - x1) / (x2 - x1)
        
        return 0.0
    
    def calculate_score(self, total_time_ms: int, best_time_ms: int) -> float:
        """Calculate final score according to specification"""
        if best_time_ms is None:
            return float('inf')  # No successful run
        
        return (1/30) * total_time_ms + best_time_ms
    
    def update_game_state(self, game_uuid: str, new_state: Dict[str, Any]):
        """Update game state with new information from the API response"""
        if game_uuid not in self.games:
            logger.warning(f"Game {game_uuid} not found for update")
            return
            
        game = self.games[game_uuid]
        
        # Ensure position is properly initialized
        if 'position' not in game or not isinstance(game['position'], tuple):
            game['position'] = (0, 0)
        
        # Update state fields
        if 'sensor_data' in new_state:
            game['sensor_data'] = new_state['sensor_data']
        if 'total_time_ms' in new_state:
            game['total_time_ms'] = new_state['total_time_ms']
        if 'goal_reached' in new_state:
            game['goal_reached'] = new_state['goal_reached']
        if 'best_time_ms' in new_state:
            game['best_time_ms'] = new_state['best_time_ms']
        if 'run_time_ms' in new_state:
            game['run_time_ms'] = new_state['run_time_ms']
        if 'run' in new_state:
            game['run'] = new_state['run']
        if 'momentum' in new_state:
            game['momentum'] = new_state['momentum']
            
        # Update position based on movement
        self._update_position_from_momentum(game)
        
        # Check if we reached the goal
        if self._is_in_goal_area(game['position']):
            game['goal_reached'] = True
            if game['best_time_ms'] is None or game['run_time_ms'] < game['best_time_ms']:
                game['best_time_ms'] = game['run_time_ms']
            logger.info(f"Goal reached! Run time: {game['run_time_ms']}ms")
        
        # Check if we're back at start for a new run
        if game['position'] == (0, 0) and game['momentum'] == 0:
            game['current_run_started'] = False
            logger.info(f"Back at start, ready for new run")
    
    def _update_position_from_momentum(self, game: Dict[str, Any]):
        """Update position based on current momentum and orientation"""
        momentum = game['momentum']
        orientation = game['orientation']
        position = game['position']
        
        if momentum == 0:
            return
            
        # Ensure position is a valid tuple
        if not isinstance(position, tuple) or len(position) != 2:
            logger.error(f"Invalid position format: {position}, type: {type(position)}")
            game['position'] = (0, 0)  # Reset to start position
            position = (0, 0)
            
        # Calculate movement based on orientation and momentum
        dx = 0
        dy = 0
        
        if orientation == 0:  # North
            dy = -1
        elif orientation == 45:  # Northeast
            dx = 1
            dy = -1
        elif orientation == 90:  # East
            dx = 1
        elif orientation == 135:  # Southeast
            dx = 1
            dy = 1
        elif orientation == 180:  # South
            dy = 1
        elif orientation == 225:  # Southwest
            dx = -1
            dy = 1
        elif orientation == 270:  # West
            dx = -1
        elif orientation == 315:  # Northwest
            dx = -1
            dy = -1
            
        # Apply momentum (simplified - assumes half-steps)
        steps = abs(momentum)
        new_x = position[0] + (dx * steps)
        new_y = position[1] + (dy * steps)
        
        # Keep within bounds
        new_x = max(0, min(15, new_x))
        new_y = max(0, min(15, new_y))
        
        game['position'] = (new_x, new_y)
    
    def _is_in_goal_area(self, position: Tuple[int, int]) -> bool:
        """Check if position is in the 2x2 goal area at center"""
        # Ensure position is a valid tuple
        if not isinstance(position, tuple) or len(position) != 2:
            logger.error(f"Invalid position in _is_in_goal_area: {position}")
            return False
            
        x, y = position
        # Goal is 2x2 at center (7,7) to (8,8)
        return 7 <= x <= 8 and 7 <= y <= 8
    
    def get_game_stats(self, game_uuid: str) -> Dict[str, Any]:
        """Get current game statistics"""
        if game_uuid not in self.games:
            return {}
            
        game = self.games[game_uuid]
        return {
            'position': game['position'],
            'orientation': game['orientation'],
            'momentum': game['momentum'],
            'run': game['run'],
            'run_time_ms': game['run_time_ms'],
            'best_time_ms': game['best_time_ms'],
            'goal_reached': game['goal_reached'],
            'total_time_ms': game['total_time_ms'],
            'time_remaining': game['time_budget'] - game['total_time_ms']
        }

# Global game manager
game_manager = MicromouseController()

@app.route('/micro-mouse', methods=['POST'])
def micromouse():
    """
    Main endpoint for micromouse controller
    Handles game state updates and returns movement instructions
    """
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({'error': 'Empty request body'}), 400
            
        game_uuid = payload.get('game_uuid')
        if not game_uuid:
            return jsonify({'error': 'Missing game_uuid'}), 400
            
        # Check if this is a new game or update
        if game_uuid not in game_manager.games:
            # New game - initialize
            logger.info(f"Initializing new game {game_uuid} with payload: {payload}")
            game_manager.start_new_game(
                game_uuid=game_uuid,
                sensor_data=payload.get('sensor_data', [0, 0, 0, 0, 0]),
                total_time_ms=payload.get('total_time_ms', 0),
                goal_reached=payload.get('goal_reached', False),
                best_time_ms=payload.get('best_time_ms'),
                run_time_ms=payload.get('run_time_ms', 0),
                run=payload.get('run', 0),
                momentum=payload.get('momentum', 0)
            )
        else:
            # Update existing game
            logger.info(f"Updating existing game {game_uuid} with payload: {payload}")
            try:
                game_manager.update_game_state(game_uuid, payload)
            except Exception as e:
                logger.error(f"Error updating game state: {str(e)}")
                # Continue with instruction generation even if update fails
        
        # Generate next instructions
        try:
            instructions, end_flag = game_manager.get_next_instructions(game_uuid)
        except Exception as e:
            logger.error(f"Error generating instructions: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            instructions = []
            end_flag = True
        
        # Add thinking time if we have instructions
        if instructions and not end_flag:
            # The 50ms thinking time is handled by the API
            pass
            
        response = {
            'instructions': instructions,
            'end': end_flag
        }
        
        logger.info(f"Micromouse {game_uuid}: instructions={instructions}, end={end_flag}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in micromouse endpoint: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/micro-mouse/stats/<game_uuid>', methods=['GET'])
def get_micromouse_stats(game_uuid):
    """Get statistics for a specific micromouse game"""
    try:
        stats = game_manager.get_game_stats(game_uuid)
        if not stats:
            return jsonify({'error': 'Game not found'}), 404
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting micromouse stats: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/micro-mouse/debug/<game_uuid>', methods=['GET'])
def get_micromouse_debug(game_uuid):
    """Get debug information for a specific micromouse game"""
    try:
        if game_uuid not in game_manager.games:
            return jsonify({'error': 'Game not found'}), 404
        
        game = game_manager.games[game_uuid]
        debug_info = {
            'position': game['position'],
            'position_type': str(type(game['position'])),
            'orientation': game['orientation'],
            'momentum': game['momentum'],
            'sensor_data': game['sensor_data'],
            'maze_map': dict(game['maze_map']),
            'visited_cells': list(game['visited_cells']),
            'run': game['run'],
            'goal_reached': game['goal_reached']
        }
        return jsonify(debug_info)
    except Exception as e:
        logger.error(f"Error getting micromouse debug info: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
