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
            logger.info(f"Empty or None test_case provided for game {game_id}")
            raise ValueError("test_case cannot be None or empty")
            
        # Validate test_case structure
        if not isinstance(test_case, dict):
            logger.info(f"Invalid test_case type for game {game_id}: {type(test_case)}")
            raise ValueError(f"test_case must be a dictionary, got {type(test_case)}")
            
        # Handle None or missing crows
        crows_data = test_case.get('crows', [])
        if not crows_data:
            logger.warning(f"No crows data in test_case for game {game_id}")
            crows_data = []
        elif not isinstance(crows_data, list):
            logger.info(f"Invalid crows data type for game {game_id}: {type(crows_data)}")
            raise ValueError(f"crows must be a list, got {type(crows_data)}")
            
        # Safely process crows, filtering out None values
        crows = {}
        for crow in crows_data:
            if (crow and isinstance(crow, dict) and 
                'id' in crow and 'x' in crow and 'y' in crow):
                try:
                    x, y = int(crow['x']), int(crow['y'])
                    crows[crow['id']] = {'x': x, 'y': y}
                except (ValueError, TypeError):
                    continue
        
        if not crows:
            raise ValueError("No valid crows found in test_case")
        
        # Quick validation
        grid_size = max(10, int(test_case.get('length_of_grid', 10)))
        num_walls = max(0, int(test_case.get('num_of_walls', 0)))
        
        self.games[game_id] = {
            'crows': crows,
            'grid_size': grid_size,
            'num_walls': num_walls,
            'discovered_walls': set(),
            'explored_cells': set(),
            'scan_results': {},  # Store scan results for each position
            'move_count': 0,
            'game_complete': False,
            'max_moves': min(50, max(20, num_walls * 2)),  # Much more aggressive limit
            'recent_moves': deque(maxlen=5),  # Shorter memory to detect loops faster
            'stuck_count': 0  # Count consecutive moves to same area
        }
        # Game initialized successfully
        
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
        # Check completion status
        walls_found = len(game_state['discovered_walls'])
        total_walls = game_state['num_walls']
        moves_used = game_state['move_count']
        
        # Only submit when we actually found all walls
        if walls_found >= total_walls:
            return None, 'submit', None
        
        # More reasonable move limits based on problem size
        grid_size = game_state.get('grid_size', 10)
        reasonable_limit = min(grid_size * grid_size, total_walls * 5)  # Much more generous
        
        # Only submit if we've used too many moves
        if moves_used >= reasonable_limit:
            return None, 'submit', None
        
        # Priority 1: Scan unexplored areas that are likely to have walls
        best_scan_crow = None
        best_scan_value = 0
        
        for crow_id, crow_pos in crows.items():
            if not crow_pos or not isinstance(crow_pos, dict):
                continue
            x, y = crow_pos['x'], crow_pos['y']
            
            # Only scan if not already scanned
            if (x, y) not in game_state['scan_results']:
                scan_value = self._calculate_scan_value(x, y, game_state)
                if scan_value > best_scan_value:
                    best_scan_value = scan_value
                    best_scan_crow = crow_id
        
        # If we found a good scanning opportunity, take it
        if best_scan_crow and best_scan_value > 5:
            return best_scan_crow, 'scan', None
        
        # Priority 2: Move to unexplored areas
        best_move_crow = None
        best_move_direction = None
        best_move_score = 0
        
        for crow_id, crow_pos in crows.items():
            if not crow_pos or not isinstance(crow_pos, dict):
                continue
                
            x, y = crow_pos.get('x'), crow_pos.get('y')
            if x is None or y is None:
                continue
            
            # Try all directions
            for direction in ['N', 'E', 'S', 'W']:
                if self._is_valid_move(crow_pos, direction, game_state):
                    new_x, new_y = self._get_new_position(x, y, direction)
                    move_score = self._calculate_move_score(new_x, new_y, game_state)
                    
                    if move_score > best_move_score:
                        best_move_score = move_score
                        best_move_crow = crow_id
                        best_move_direction = direction
        
        # Make the best move if we found one
        if best_move_crow and best_move_direction and best_move_score > 0:
            return best_move_crow, 'move', best_move_direction
        
        # Priority 3: Scan current positions if nothing else to do
        for crow_id, crow_pos in crows.items():
            if not crow_pos or not isinstance(crow_pos, dict):
                continue
            x, y = crow_pos['x'], crow_pos['y']
            
            if (x, y) not in game_state['scan_results']:
                return crow_id, 'scan', None
        
        # If we still haven't found all walls but no good actions, submit what we have
        return None, 'submit', None
    
    def _quick_scan_value(self, x, y, game_state):
        """Fast scan value calculation"""
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return 0
            
        # Count unexplored cells in 3x3 area (smaller for speed)
        unexplored = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                check_x, check_y = x + dx, y + dy
                if (0 <= check_x < self.grid_size and 0 <= check_y < self.grid_size):
                    if (check_x, check_y) not in game_state['explored_cells']:
                        unexplored += 1
        
        return unexplored * 3
    
    def _calculate_move_score(self, x, y, game_state):
        """Calculate the value of moving to position (x, y)"""
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return 0
            
        # No value for explored cells or walls
        if (x, y) in game_state['explored_cells']:
            return 1  # Very low score for explored
        if (x, y) in game_state['discovered_walls']:
            return 0  # No score for walls
            
        # Base score for unexplored cells
        score = 10
        
        # Bonus for cells that can give us good scan coverage
        scan_potential = 0
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                scan_x, scan_y = x + dx, y + dy
                if (0 <= scan_x < self.grid_size and 0 <= scan_y < self.grid_size):
                    if (scan_x, scan_y) not in game_state['explored_cells']:
                        scan_potential += 1
        
        score += scan_potential
        
        # Bonus for frontier exploration (adjacent to explored areas)
        adjacent_to_explored = False
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                adj_x, adj_y = x + dx, y + dy
                if (adj_x, adj_y) in game_state['explored_cells']:
                    adjacent_to_explored = True
                    break
            if adjacent_to_explored:
                break
        
        if adjacent_to_explored:
            score += 5
        
        return score
        
        
                
        
        
        
        
        
            
    def _calculate_scan_value(self, x, y, game_state):
        """Calculate the value of scanning at position (x, y)"""
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return 0
            
        # Skip if already scanned
        if (x, y) in game_state['scan_results']:
            return 0
            
        # Calculate value based on unexplored area in 5x5 scan range
        value = 0
        for dx in range(-2, 3):  # Full 5x5 area
            for dy in range(-2, 3):
                check_x, check_y = x + dx, y + dy
                if (0 <= check_x < self.grid_size and 0 <= check_y < self.grid_size):
                    if (check_x, check_y) not in game_state['explored_cells']:
                        # Higher value for cells further from explored areas
                        if game_state['explored_cells']:
                            min_dist = min(abs(check_x - ex) + abs(check_y - ey) 
                                         for ex, ey in game_state['explored_cells'])
                            value += min(5, 1 + min_dist)
                        else:
                            value += 3
        
        # Bonus for edge areas (more likely to have walls)
        if x < 2 or x >= self.grid_size - 2 or y < 2 or y >= self.grid_size - 2:
            value += 5
        
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
    start_time = time.time()  # Track execution time for timeout prevention
    
    try:
        # Parse JSON payload
        try:
            payload = request.get_json(force=True)
        except Exception as e:
            logger.info(f"Failed to parse JSON: {e}")
            return jsonify({'error': 'Invalid JSON in request body'}), 400
            
        if not payload:
            logger.info("Empty request body received")
            return jsonify({'error': 'Empty request body'}), 400
        
        # DETAILED PAYLOAD LOGGING FOR TRAINING
        logger.info("="*80)
        logger.info("FOG OF WALL - DETAILED PAYLOAD ANALYSIS")
        logger.info("="*80)
        
        # Log full payload structure
        logger.info(f"Full payload keys: {list(payload.keys())}")
        logger.info(f"Payload size: {len(str(payload))} characters")
        
        challenger_id = payload.get('challenger_id')
        game_id = payload.get('game_id')
        
        logger.info(f"Challenger ID: {challenger_id}")
        logger.info(f"Game ID: {game_id}")
        
        if not challenger_id or not game_id:
            logger.info("Missing challenger_id or game_id")
            return jsonify({'error': 'Missing challenger_id or game_id'}), 400
        
        # Log test_case details if present
        if 'test_case' in payload and payload['test_case'] is not None:
            test_case = payload['test_case']
            logger.info("NEW TEST CASE DETECTED!")
            logger.info(f"Test case type: {type(test_case)}")
            logger.info(f"Test case keys: {list(test_case.keys()) if isinstance(test_case, dict) else 'Not a dict'}")
            
            if isinstance(test_case, dict):
                crows_data = test_case.get('crows', [])
                logger.info(f"Number of crows: {len(crows_data) if crows_data else 0}")
                
                # Log each crow's details
                for i, crow in enumerate(crows_data[:3]):  # Log first 3 crows to avoid spam
                    logger.info(f"Crow {i}: {crow}")
                
                if len(crows_data) > 3:
                    logger.info(f"... and {len(crows_data) - 3} more crows")
                    
                # Log maze dimensions if available
                if 'maze_height' in test_case and 'maze_width' in test_case:
                    logger.info(f"Maze dimensions: {test_case['maze_width']} x {test_case['maze_height']}")
        
        # Log previous_action details if present
        if 'previous_action' in payload and payload['previous_action'] is not None:
            prev_action = payload['previous_action']
            logger.info("PREVIOUS ACTION RESPONSE:")
            logger.info(f"Previous action type: {type(prev_action)}")
            logger.info(f"Previous action keys: {list(prev_action.keys()) if isinstance(prev_action, dict) else 'Not a dict'}")
            
            if isinstance(prev_action, dict):
                action_type = prev_action.get('action_type')
                logger.info(f"Action type: {action_type}")
                
                if action_type == 'scan':
                    scan_result = prev_action.get('scan_result', {})
                    walls = scan_result.get('walls', [])
                    logger.info(f"Scan result - {len(walls)} walls found")
                    logger.info(f"Sample walls: {walls[:5] if walls else 'None'}")
                
                elif action_type == 'move':
                    move_result = prev_action.get('move_result', {})
                    logger.info(f"Move result: {move_result}")
        
        logger.info("-" * 80)
        
        # Timeout check - only if we've been running too long
        if time.time() - start_time > 25.0:  # Much more generous 25 second timeout
            logger.warning(f"Timeout reached for game {game_id}, submitting current progress")
            if game_id in game_manager.games:
                discovered_walls = game_manager.get_discovered_walls(game_id)
                logger.info(f"Submitting {len(discovered_walls)} discovered walls due to timeout")
                return jsonify({
                    'challenger_id': challenger_id,
                    'game_id': game_id,
                    'action_type': 'submit',
                    'submission': discovered_walls
                })
            else:
                logger.info("Timeout and no game state found")
                return jsonify({'error': 'Timeout and no game state'}), 500
        
        # Check if this is an initial request with valid test_case data
        has_test_case = 'test_case' in payload and payload['test_case'] is not None
        has_previous_action = 'previous_action' in payload and payload['previous_action'] is not None
            
        if has_test_case:
            test_case = payload['test_case']
            
            # Quick validation
            if not isinstance(test_case, dict):
                return jsonify({'error': 'Invalid test_case data'}), 400
                
            crows_data = test_case.get('crows', [])
            if not crows_data:
                return jsonify({'error': 'No crows data'}), 400
                
            # Initialize new game quickly
            try:
                game_manager.start_new_game(game_id, test_case)
            except Exception as e:
                return jsonify({'error': f'Failed to start game: {str(e)}'}), 400
            
            # Quick action - start with first crow scan
            game_state = game_manager.games[game_id]
            crows = game_state['crows']
            
            if not crows:
                return jsonify({'error': 'No crows available'}), 400
                
            # Just use first crow for initial scan
            first_crow_id = list(crows.keys())[0]
            return jsonify({
                'challenger_id': challenger_id,
                'game_id': game_id,
                'crow_id': first_crow_id,
                'action_type': 'scan'
            })
            
        # Handle previous action result quickly
        previous_action = payload.get('previous_action')
        if not previous_action:
            return jsonify({'error': 'Invalid request: must provide either test_case or previous_action'}), 400
            
        action_type = previous_action.get('your_action')
        crow_id = previous_action.get('crow_id')
        
        if not action_type or not crow_id:
            return jsonify({'error': 'Missing action_type or crow_id in previous_action'}), 400
            
        # Check if game exists
        if game_id not in game_manager.games:
            return jsonify({'error': 'Game not found'}), 404
        
        # Process action results quickly
        if action_type == 'move':
            move_result = previous_action.get('move_result')
            if move_result and isinstance(move_result, (list, dict)):
                if isinstance(move_result, list) and len(move_result) == 2:
                    new_x, new_y = move_result
                elif isinstance(move_result, dict):
                    new_x = move_result.get('x')
                    new_y = move_result.get('y')
                else:
                    new_x, new_y = None, None
                
                if (new_x is not None and new_y is not None and 
                    isinstance(new_x, (int, float)) and isinstance(new_y, (int, float))):
                    game_manager.update_crow_position(game_id, crow_id, int(new_x), int(new_y))
                    
        elif action_type == 'scan':
            scan_result = previous_action.get('scan_result')
            crow_pos = game_manager.get_crow_position(game_id, crow_id)
            if (crow_pos and scan_result and isinstance(scan_result, list) and
                len(scan_result) == 5 and all(isinstance(row, list) and len(row) == 5 for row in scan_result)):
                game_manager.add_scan_result(game_id, crow_id, crow_pos['x'], crow_pos['y'], scan_result)
                
        # Check if game is complete or move limit reached
        game_state = game_manager.games[game_id]
        
        # More balanced timeout handling
        walls_found = len(game_state['discovered_walls'])
        total_walls = game_state['num_walls']
        moves_used = game_state['move_count']
        grid_size = game_state.get('grid_size', 10)
        
        # More reasonable limits based on problem complexity
        reasonable_move_limit = min(grid_size * grid_size, total_walls * 6)
        
        # Only submit early if we found all walls or used way too many moves
        should_submit = (
            walls_found >= total_walls or 
            moves_used >= reasonable_move_limit
        )
        
        if should_submit:
            discovered_walls = game_manager.get_discovered_walls(game_id)
            logger.info(f"Game {game_id} completed: walls={len(discovered_walls)}/{total_walls}, moves={moves_used}")
            
            # LOG SUBMISSION RESPONSE
            logger.info("="*60)
            logger.info("SUBMITTING FINAL ANSWER")
            logger.info(f"Game: {game_id}")
            logger.info(f"Total walls found: {len(discovered_walls)}")
            logger.info(f"Moves used: {moves_used}")
            logger.info(f"Sample walls: {discovered_walls[:10] if discovered_walls else 'None'}")
            logger.info("="*60)
            
            return jsonify({
                'challenger_id': challenger_id,
                'game_id': game_id,
                'action_type': 'submit',
                'submission': discovered_walls
            })
            
        # Get next action with timeout protection
        try:
            # Final timeout check before algorithm - more generous
            if time.time() - start_time > 20.0:  # 20 second timeout
                discovered_walls = game_manager.get_discovered_walls(game_id)
                return jsonify({
                    'challenger_id': challenger_id,
                    'game_id': game_id,
                    'action_type': 'submit',
                    'submission': discovered_walls
                })
                
            # Very fast algorithm execution
            grid_size = game_state.get('grid_size', 10)
            explorer = MazeExplorer(grid_size)
            next_crow, next_action, direction = explorer.get_next_action(game_state, crows)
            
        except Exception as e:
            # Immediate fallback: submit what we have
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
            logger.info("="*40)
            logger.info(f"SENDING SCAN ACTION")
            logger.info(f"Game: {game_id}, Crow: {next_crow}")
            logger.info("="*40)
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
            
            logger.info("="*40)
            logger.info(f"SENDING MOVE ACTION")
            logger.info(f"Game: {game_id}, Crow: {next_crow}, Direction: {direction}")
            logger.info("="*40)
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
        logger.info(f"Error in fog_of_wall endpoint: {str(e)}")
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
