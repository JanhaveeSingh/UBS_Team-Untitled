import os
import sys
import logging
from flask import request, jsonify
import json
from collections import deque, defaultdict
import heapq
import math
import time

# Add parent directory to path to allow importing routes module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)

class FogOfWallGame:
    """
    Game state manager for Fog of Wall maze exploration
    """
    
    def __init__(self):
        self.games = {}  # Store game states by game_id
        
    def start_new_game(self, game_id, test_case):
        """Initialize a new game with test case data"""
        # Handle None or missing test_case
        if not test_case:
            logger.error(f"Empty or None test_case provided for game {game_id}")
            raise ValueError("test_case cannot be None or empty")
            
        # Validate test_case structure
        if not isinstance(test_case, dict):
            logger.error(f"Invalid test_case type for game {game_id}: {type(test_case)}")
            raise ValueError(f"test_case must be a dictionary, got {type(test_case)}")
            
        # Handle None or missing crows
        crows_data = test_case.get('crows', [])
        if not crows_data:
            logger.warning(f"No crows data in test_case for game {game_id}")
            crows_data = []
        elif not isinstance(crows_data, list):
            logger.error(f"Invalid crows data type for game {game_id}: {type(crows_data)}")
            raise ValueError(f"crows must be a list, got {type(crows_data)}")
            
        # Safely process crows, filtering out None values
        crows = {}
        for i, crow in enumerate(crows_data):
            if crow is None:
                logger.warning(f"Skipping None crow at index {i} in game {game_id}")
                continue
            if not isinstance(crow, dict):
                logger.warning(f"Skipping invalid crow at index {i} in game {game_id}: {type(crow)}")
                continue
            if 'id' not in crow or 'x' not in crow or 'y' not in crow:
                logger.warning(f"Skipping crow at index {i} in game {game_id} missing required fields: {crow}")
                continue
            try:
                x, y = int(crow['x']), int(crow['y'])
                crows[crow['id']] = {'x': x, 'y': y}
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping crow at index {i} in game {game_id} with invalid coordinates: {e}")
                continue
        
        if not crows:
            logger.error(f"No valid crows found in test_case for game {game_id}")
            raise ValueError("No valid crows found in test_case")
        
        # Validate grid size
        grid_size = test_case.get('length_of_grid', 10)
        try:
            grid_size = int(grid_size)
            if grid_size <= 0:
                logger.warning(f"Invalid grid_size {grid_size} for game {game_id}, using default 10")
                grid_size = 10
        except (ValueError, TypeError):
            logger.warning(f"Invalid grid_size type for game {game_id}, using default 10")
            grid_size = 10
            
        # Validate number of walls
        num_walls = test_case.get('num_of_walls', 0)
        try:
            num_walls = int(num_walls)
            if num_walls < 0:
                logger.warning(f"Invalid num_walls {num_walls} for game {game_id}, using 0")
                num_walls = 0
        except (ValueError, TypeError):
            logger.warning(f"Invalid num_walls type for game {game_id}, using 0")
            num_walls = 0
        
        self.games[game_id] = {
            'crows': crows,
            'grid_size': grid_size,
            'num_walls': num_walls,
            'discovered_walls': set(),
            'explored_cells': set(),
            'scan_results': {},  # Store scan results for each position
            'move_count': 0,
            'game_complete': False,
            'max_moves': grid_size * grid_size,  # Use full grid size for move limit
            'recent_moves': deque(maxlen=10),  # Track recent moves to prevent loops
            'stuck_count': 0  # Count consecutive moves to same area
        }
        logger.info(f"Started new game {game_id} with {len(crows)} crows, grid_size={grid_size}, num_walls={num_walls}")
        
    def get_crow_position(self, game_id, crow_id):
        """Get current position of a crow"""
        if game_id not in self.games:
            return None
        return self.games[game_id]['crows'].get(crow_id)
        
    def update_crow_position(self, game_id, crow_id, new_x, new_y):
        """Update crow position after a move"""
        if game_id in self.games and crow_id in self.games[game_id]['crows']:
            old_pos = self.games[game_id]['crows'][crow_id]
            self.games[game_id]['crows'][crow_id] = {'x': new_x, 'y': new_y}
            self.games[game_id]['move_count'] += 1
            
            # Track recent moves for loop detection
            move_key = f"{crow_id}:{old_pos['x']},{old_pos['y']}->{new_x},{new_y}"
            self.games[game_id]['recent_moves'].append(move_key)
            
    def add_scan_result(self, game_id, crow_id, x, y, scan_data):
        """Process and store scan results"""
        if game_id not in self.games:
            return
            
        if not scan_data or not isinstance(scan_data, list):
            return
            
        game = self.games[game_id]
        game['move_count'] += 1
        
        # Mark the center cell as explored
        game['explored_cells'].add((x, y))
        
        # Process the 5x5 scan grid
        for i, row in enumerate(scan_data):
            if not isinstance(row, list):
                continue
            for j, cell in enumerate(row):
                # Convert relative position to absolute coordinates
                scan_x = x + (j - 2)  # j-2 because center is at [2][2]
                scan_y = y + (i - 2)  # i-2 because center is at [2][2]
                
                # Check bounds first
                if 0 <= scan_x < game['grid_size'] and 0 <= scan_y < game['grid_size']:
                    if cell == 'W':  # Wall found
                        game['discovered_walls'].add((scan_x, scan_y))
                    elif cell == '_':  # Empty cell - mark as explored
                        game['explored_cells'].add((scan_x, scan_y))
                        
        # Store scan result for this position
        game['scan_results'][(x, y)] = scan_data
        
    def get_discovered_walls(self, game_id):
        """Get all discovered walls in submission format"""
        if game_id not in self.games:
            return []
        return [f"{x}-{y}" for x, y in self.games[game_id]['discovered_walls']]
        
    def is_game_complete(self, game_id):
        """Check if all walls have been discovered"""
        if game_id not in self.games:
            return False
        game = self.games[game_id]
        return len(game['discovered_walls']) >= game['num_walls']
        
    def get_game_stats(self, game_id):
        """Get current game statistics"""
        if game_id not in self.games:
            return None
        game = self.games[game_id]
        return {
            'walls_discovered': len(game['discovered_walls']),
            'total_walls': game['num_walls'],
            'cells_explored': len(game['explored_cells']),
            'move_count': game['move_count'],
            'completion_percentage': len(game['discovered_walls']) / game['num_walls'] * 100
        }

class MazeExplorer:
    """
    Intelligent maze exploration strategy with multi-crow coordination
    """
    
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.explored = set()
        self.walls = set()
        self.frontier = set()
        self.crow_assignments = {}  # Track which areas each crow is exploring
        
    def get_next_action(self, game_state, crows):
        """
        Determine the best next action for any crow using optimized exploration
        Returns (crow_id, action_type, direction_or_none)
        """
        # Check if we should submit early (found enough walls or running out of moves)
        walls_found = len(game_state['discovered_walls'])
        total_walls = game_state['num_walls']
        moves_used = game_state['move_count']
        max_moves = game_state['max_moves']
        
        # Check for loops (repeated move patterns)
        recent_moves = game_state.get('recent_moves', deque())
        if len(recent_moves) >= 6:
            # Check if we're repeating the same 3-move pattern
            last_3 = list(recent_moves)[-3:]
            if len(set(last_3)) == 1:  # All 3 moves are identical
                logger.warning(f"Detected loop pattern, submitting early: {last_3}")
                return None, 'submit', None
        
        # Aggressive submission strategy for better efficiency
        # Submit early if we found all walls or are running out of moves
        if (walls_found >= total_walls or 
            moves_used >= max_moves):
            logger.info(f"Submitting: walls={walls_found}/{total_walls}, moves={moves_used}/{max_moves}")
            return None, 'submit', None
        
        # Strategy: Multi-crow coordinated exploration for maximum wall discovery
        
        # First, find the best scanning opportunity across all crows
        best_scan_crow = None
        best_scan_score = -1
        
        for crow_id, crow_pos in crows.items():
            if not crow_pos or not isinstance(crow_pos, dict):
                continue
            x, y = crow_pos['x'], crow_pos['y']
            
            # Skip if already scanned this position
            if (x, y) in game_state['scan_results']:
                continue
            
            # Calculate scan value for this position
            scan_score = self._calculate_scan_value(x, y, game_state)
            if scan_score > best_scan_score:
                best_scan_score = scan_score
                best_scan_crow = crow_id
                
        # Only scan if the score is high enough (avoid wasteful scanning)
        if best_scan_crow and best_scan_score > 3:
            logger.info(f"Scanning with crow {best_scan_crow} at position {crows[best_scan_crow]} (score: {best_scan_score})")
            return best_scan_crow, 'scan', None
        
        # If no good scanning opportunities, coordinate movement across all crows
        # Prioritize moving to unexplored areas with high wall potential
        
        # Multi-crow coordinated movement strategy
        # Find the best move across all crows, prioritizing different exploration areas
        best_crow = None
        best_direction = None
        best_score = -1
        
        # Track which crows have been considered to avoid clustering
        considered_crows = set()
        
        for crow_id, crow_pos in crows.items():
            if not crow_pos or not isinstance(crow_pos, dict):
                continue
                
            x = crow_pos.get('x')
            y = crow_pos.get('y')
            
            if x is None or y is None:
                continue
            
            # Try each direction and score the move
            for direction in ['N', 'S', 'E', 'W']:
                if not self._is_valid_move(crow_pos, direction, game_state):
                    continue
                    
                new_x, new_y = self._get_new_position(x, y, direction)
                
                # Calculate score for this move
                score = self._calculate_move_score(new_x, new_y, game_state)
                
                # Bonus for crows that haven't been used recently
                if crow_id not in considered_crows:
                    score += 5
                
                # Penalty for moving to recently explored areas (unless high value)
                if (new_x, new_y) in game_state['explored_cells'] and score < 10:
                    score *= 0.5  # Reduce score but don't eliminate
                
                if score > best_score:
                    best_score = score
                    best_crow = crow_id
                    best_direction = direction
        
        if best_crow and best_direction:
            logger.info(f"Moving crow {best_crow} {best_direction} from {crows[best_crow]} (score: {best_score})")
            return best_crow, 'move', best_direction
        
        # If no good moves found, try any valid move (even to explored areas)
        for crow_id, crow_pos in crows.items():
            if not crow_pos or not isinstance(crow_pos, dict):
                continue
                
            x = crow_pos.get('x')
            y = crow_pos.get('y')
            
            if x is None or y is None:
                continue
            
            # Try each direction for any valid move
            for direction in ['N', 'S', 'E', 'W']:
                if not self._is_valid_move(crow_pos, direction, game_state):
                    continue
                    
                new_x, new_y = self._get_new_position(x, y, direction)
                
                # Even if explored, try to move there if it's not a wall
                logger.info(f"Fallback move: crow {crow_id} {direction} to explored area")
                return crow_id, 'move', direction
        
        # If absolutely no moves possible, submit what we have
        # But first, try one more scan if we haven't found all walls
        if walls_found < total_walls:
            for crow_id, crow_pos in crows.items():
                if not crow_pos or not isinstance(crow_pos, dict):
                    continue
                x, y = crow_pos['x'], crow_pos['y']
                if (x, y) not in game_state['scan_results']:
                    logger.info(f"Last attempt: scanning with crow {crow_id} at position {crow_pos}")
                    return crow_id, 'scan', None
        
        logger.warning("No valid moves found, submitting current results")
        return None, 'submit', None
    
    def _calculate_move_score(self, x, y, game_state):
        """Calculate how valuable it would be to move to position (x, y)"""
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return 0
            
        # Check if position is already explored
        if (x, y) in game_state['explored_cells']:
            return 1  # Small score for re-exploration if needed
            
        # Check if position is a known wall
        if (x, y) in game_state['discovered_walls']:
            return 0
            
        # Base score for unexplored position
        score = 30
        
        # Check for nearby unexplored areas
        unexplored_nearby = 0
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                check_x, check_y = x + dx, y + dy
                if (0 <= check_x < self.grid_size and 0 <= check_y < self.grid_size):
                    if (check_x, check_y) not in game_state['explored_cells']:
                        unexplored_nearby += 1
        
        score += unexplored_nearby * 2
        
        # Distance calculation for frontier exploration
        if game_state['explored_cells']:
            min_distance = min(abs(x - ex) + abs(y - ey) 
                             for ex, ey in game_state['explored_cells'])
            # Bonus for being on the frontier (distance 1-3 from explored)
            if 1 <= min_distance <= 3:
                score += 10
        else:
            score += 20
        
        return score
        
        
                
        
        
        
        
        
            
    def _calculate_scan_value(self, x, y, game_state):
        """Calculate how valuable it would be to scan at position (x, y)"""
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return 0
            
        # Skip if already scanned
        if (x, y) in game_state['scan_results']:
            return 0
            
        value = 0
        
        # Count unexplored cells in 5x5 area
        unexplored_count = 0
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                check_x, check_y = x + dx, y + dy
                if (0 <= check_x < self.grid_size and 0 <= check_y < self.grid_size):
                    if (check_x, check_y) not in game_state['explored_cells']:
                        unexplored_count += 1
        
        # Higher value for areas with more unexplored cells
        value += unexplored_count * 4
        
        # Bonus for positions near discovered walls (wall clustering)
        if game_state['discovered_walls']:
            wall_proximity = sum(1 for wall_x, wall_y in game_state['discovered_walls']
                               if abs(x - wall_x) + abs(y - wall_y) <= 3)
            value += wall_proximity * 2
            
        return value
        
    def _is_valid_move(self, crow_pos, direction, game_state):
        """Check if a move in the given direction is valid"""
        if not crow_pos or not isinstance(crow_pos, dict):
            return False
            
        x = crow_pos.get('x')
        y = crow_pos.get('y')
        
        if x is None or y is None:
            return False
            
        new_x, new_y = self._get_new_position(x, y, direction)
        
        if new_x is None or new_y is None:
            return False
        
        # Check bounds
        if not (0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size):
            return False
        
        # Check if the destination is a known wall
        if (new_x, new_y) in game_state['discovered_walls']:
            return False
            
        return True
        
    def _get_new_position(self, x, y, direction):
        """Get new position after moving in given direction"""
        if x is None or y is None:
            return None, None
            
        if direction == 'N':
            return x, y - 1
        elif direction == 'S':
            return x, y + 1
        elif direction == 'E':
            return x + 1, y
        elif direction == 'W':
            return x - 1, y
        return x, y

# Global game manager
game_manager = FogOfWallGame()

@app.route('/fog-of-wall', methods=['POST'])
def fog_of_wall():
    """
    Main endpoint for Fog of Wall game
    Handles initial setup, move results, scan results, and submissions
    """
    try:
        # Fast JSON parsing without extensive logging for production
        try:
            payload = request.get_json(force=True)
        except Exception as e:
            return jsonify({'error': 'Invalid JSON in request body'}), 400
            
        if not payload:
            return jsonify({'error': 'Empty request body'}), 400
            
        challenger_id = payload.get('challenger_id')
        game_id = payload.get('game_id')
        
        # Minimal logging for production performance
        has_test_case = 'test_case' in payload and payload['test_case'] is not None and payload['test_case'] != 'null'
        has_previous_action = 'previous_action' in payload and payload['previous_action'] is not None
        
        # Only log essential info to avoid slowing down responses
        logger.info(f"Request: {challenger_id}/{game_id}, test_case={has_test_case}, prev_action={has_previous_action}")
        
        if not challenger_id or not game_id:
            return jsonify({'error': 'Missing challenger_id or game_id'}), 400
            
        # Check if this is an initial request with valid test_case data
        if 'test_case' in payload and payload['test_case'] is not None and payload['test_case'] != 'null':
            test_case = payload['test_case']
            
            # Add validation for test_case
            if not isinstance(test_case, dict):
                logger.error(f"Invalid test_case type: {type(test_case)}, value: {test_case}")
                return jsonify({'error': 'Invalid test_case data - must be a dictionary'}), 400
                
            # Validate crows data before starting game
            crows_data = test_case.get('crows', [])
            if not crows_data or not isinstance(crows_data, list):
                logger.error(f"Invalid crows data: {crows_data}")
                return jsonify({'error': 'No valid crows data found in test_case'}), 400
                
            # Check if game already exists
            if game_id in game_manager.games:
                logger.warning(f"Game {game_id} already exists, restarting with new test case")
                # Restart the game with the new test case
                try:
                    game_manager.start_new_game(game_id, test_case)
                except Exception as e:
                    logger.error(f"Failed to restart game: {str(e)}")
                    return jsonify({'error': f'Failed to restart game: {str(e)}'}), 400
            else:
                # Initialize new game
                try:
                    game_manager.start_new_game(game_id, test_case)
                except Exception as e:
                    logger.error(f"Failed to start new game: {str(e)}")
                    return jsonify({'error': f'Failed to start new game: {str(e)}'}), 400
            
            # Get initial action
            game_state = game_manager.games[game_id]
            crows = game_state['crows']
            
            # Check if we have any crows
            if not crows:
                return jsonify({'error': 'No crows available'}), 400
                
            # Start with scanning at initial positions
            # Choose the crow with the best initial scan potential
            best_crow = None
            best_score = -1
            
            # Create a temporary explorer to calculate scan values
            temp_explorer = MazeExplorer(game_state['grid_size'])
            
            for crow_id, crow_pos in crows.items():
                if not crow_pos or not isinstance(crow_pos, dict):
                    continue
                x, y = crow_pos['x'], crow_pos['y']
                score = temp_explorer._calculate_scan_value(x, y, game_state)
                if score > best_score:
                    best_score = score
                    best_crow = crow_id
            
            if best_crow:
                return jsonify({
                    'challenger_id': challenger_id,
                    'game_id': game_id,
                    'crow_id': best_crow,
                    'action_type': 'scan'
                })
            else:
                # Fallback to first crow
                first_crow_id = list(crows.keys())[0]
                return jsonify({
                    'challenger_id': challenger_id,
                    'game_id': game_id,
                    'crow_id': first_crow_id,
                    'action_type': 'scan'
                })
            
        # Handle previous action result
        previous_action = payload.get('previous_action')
        if not previous_action:
            # If we don't have a test_case and no previous_action, this is an invalid request
            logger.error(f"Invalid request: no test_case and no previous_action for game {game_id}")
            return jsonify({'error': 'Invalid request: must provide either test_case or previous_action'}), 400
            
        action_type = previous_action.get('your_action')
        crow_id = previous_action.get('crow_id')
        
        # Validate that we have the required fields
        if not action_type or not crow_id:
            return jsonify({'error': 'Missing action_type or crow_id in previous_action'}), 400
            
        # Check if game exists
        if game_id not in game_manager.games:
            logger.error(f"Game {game_id} not found when processing previous action")
            return jsonify({'error': 'Game not found'}), 404
        
        if action_type == 'move':
            # Process move result
            move_result = previous_action.get('move_result')
            if move_result:
                new_x, new_y = None, None
                
                # Handle list format [x, y]
                if isinstance(move_result, list) and len(move_result) == 2:
                    new_x, new_y = move_result
                # Handle dict format {x: x, y: y} or {crow_id: id, x: x, y: y}
                elif isinstance(move_result, dict):
                    new_x = move_result.get('x')
                    new_y = move_result.get('y')
                
                # Validate coordinates are numbers
                if (new_x is not None and new_y is not None and 
                    isinstance(new_x, (int, float)) and isinstance(new_y, (int, float))):
                    game_manager.update_crow_position(game_id, crow_id, int(new_x), int(new_y))
                    logger.info(f"Updated crow {crow_id} position to ({int(new_x)}, {int(new_y)})")
                else:
                    logger.warning(f"Invalid move result coordinates: {move_result}")
            else:
                logger.warning(f"Invalid move result format: {move_result}")
                
        elif action_type == 'scan':
            # Process scan result
            scan_result = previous_action.get('scan_result')
            crow_pos = game_manager.get_crow_position(game_id, crow_id)
            if crow_pos and scan_result and isinstance(scan_result, list):
                # Validate scan result is 5x5 grid
                if len(scan_result) == 5 and all(isinstance(row, list) and len(row) == 5 for row in scan_result):
                    game_manager.add_scan_result(game_id, crow_id, crow_pos['x'], crow_pos['y'], scan_result)
                else:
                    logger.warning(f"Invalid scan result format: {scan_result}")
            else:
                logger.warning(f"Invalid scan result or crow position: scan_result={scan_result}, crow_pos={crow_pos}")
                
        # Check if game is complete or move limit reached
        game_state = game_manager.games[game_id]
        
        # More aggressive timeout handling
        walls_found = len(game_state['discovered_walls'])
        total_walls = game_state['num_walls']
        moves_used = game_state['move_count']
        max_moves = game_state['max_moves']
        
        # Aggressive submission for better efficiency
        should_submit = (
            game_manager.is_game_complete(game_id) or 
            moves_used >= max_moves
        )
        
        if should_submit:
            discovered_walls = game_manager.get_discovered_walls(game_id)
            logger.info(f"Game {game_id} completed: walls={len(discovered_walls)}/{total_walls}, moves={moves_used}/{max_moves}")
            return jsonify({
                'challenger_id': challenger_id,
                'game_id': game_id,
                'action_type': 'submit',
                'submission': discovered_walls
            })
            
        # Get next action
        if game_id not in game_manager.games:
            return jsonify({'error': 'Game not found'}), 404
            
        game_state = game_manager.games[game_id]
        if not game_state:
            return jsonify({'error': 'Game state is None'}), 500
            
        crows = game_state.get('crows', {})
        if not crows:
            return jsonify({'error': 'No crows available'}), 400
            
        grid_size = game_state.get('grid_size')
        if not grid_size:
            return jsonify({'error': 'Grid size not found'}), 500
            
        try:
            # Add timeout protection for algorithm execution
            start_time = time.time()
            explorer = MazeExplorer(grid_size)
            next_crow, next_action, direction = explorer.get_next_action(game_state, crows)
            
            # Check if algorithm took too long (should be very fast)
            execution_time = time.time() - start_time
            if execution_time > 0.5:  # If it takes more than 500ms, something's wrong
                logger.warning(f"Algorithm took {execution_time:.3f}s, submitting early")
                discovered_walls = game_manager.get_discovered_walls(game_id)
                return jsonify({
                    'challenger_id': challenger_id,
                    'game_id': game_id,
                    'action_type': 'submit',
                    'submission': discovered_walls
                })
                
        except Exception as e:
            logger.error(f"Error in get_next_action: {str(e)}")
            # Fallback: submit what we have
            discovered_walls = game_manager.get_discovered_walls(game_id)
            return jsonify({
                'challenger_id': challenger_id,
                'game_id': game_id,
                'action_type': 'submit',
                'submission': discovered_walls
            })
        
        if not next_crow or not next_action or next_action == 'submit':
            # No valid actions or submit requested, submit what we have
            discovered_walls = game_manager.get_discovered_walls(game_id)
            logger.info(f"Submitting game {game_id} with {len(discovered_walls)} walls found")
            return jsonify({
                'challenger_id': challenger_id,
                'game_id': game_id,
                'action_type': 'submit',
                'submission': discovered_walls
            })
            
        if next_action == 'scan':
            return jsonify({
                'challenger_id': challenger_id,
                'game_id': game_id,
                'crow_id': next_crow,
                'action_type': 'scan'
            })
        elif next_action == 'move':
            # Validate direction
            if direction not in ['N', 'S', 'E', 'W']:
                logger.warning(f"Invalid direction: {direction}, submitting instead")
                discovered_walls = game_manager.get_discovered_walls(game_id)
                return jsonify({
                    'challenger_id': challenger_id,
                    'game_id': game_id,
                    'action_type': 'submit',
                    'submission': discovered_walls
                })
            return jsonify({
                'challenger_id': challenger_id,
                'game_id': game_id,
                'crow_id': next_crow,
                'action_type': 'move',
                'direction': direction
            })
        else:
            # Fallback: submit current results
            discovered_walls = game_manager.get_discovered_walls(game_id)
            return jsonify({
                'challenger_id': challenger_id,
                'game_id': game_id,
                'action_type': 'submit',
                'submission': discovered_walls
            })
            
    except Exception as e:
        logger.error(f"Error in fog_of_wall endpoint: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/fog-of-wall/stats/<game_id>', methods=['GET'])
def get_game_stats(game_id):
    """Get statistics for a specific game"""
    stats = game_manager.get_game_stats(game_id)
    if stats is None:
        return jsonify({'error': 'Game not found'}), 404
    return jsonify(stats)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render deployment"""
    return jsonify({'status': 'healthy', 'service': 'fog-of-wall'})

if __name__ == "__main__":
    # Only run the app if this file is executed directly
    app.run(debug=True, port=5001)
