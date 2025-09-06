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
        self.walls = set()  # Set of wall coordinates (x1, y1, x2, y2)
        self.visited_cells = set()  # Cells we've visited
        
        # Goal location (center 2x2)
        self.goal_cells = {(7, 7), (7, 8), (8, 7), (8, 8)}
        
        # Mouse state
        self.x = 0  # Current x position
        self.y = 0  # Current y position
        self.direction = 0  # 0=North, 1=NE, 2=East, 3=SE, 4=South, 5=SW, 6=West, 7=NW
        self.momentum = 0
        
        # Direction mappings
        self.dir_names = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        self.dir_vectors = [
            (0, 1),   # North
            (1, 1),   # Northeast  
            (1, 0),   # East
            (1, -1),  # Southeast
            (0, -1),  # South
            (-1, -1), # Southwest
            (-1, 0),  # West
            (-1, 1)   # Northwest
        ]
        
        # Sensor angles relative to mouse direction
        self.sensor_angles = [-90, -45, 0, 45, 90]  # degrees relative to facing direction
        
        # Exploration strategy
        self.exploration_phase = True
        self.path_to_goal = []
        self.current_path_index = 0
        self.game_uuid = None
        
    def reset_for_new_game(self, game_uuid):
        """Reset solver state for a new game"""
        if self.game_uuid != game_uuid:
            self.game_uuid = game_uuid
            self.walls = set()
            self.visited_cells = set()
            self.x = 0
            self.y = 0
            self.direction = 0
            self.momentum = 0
            self.exploration_phase = True
            self.path_to_goal = []
            self.current_path_index = 0
            logger.info(f"Reset solver for new game: {game_uuid}")
    
    def get_sensor_directions(self) -> List[int]:
        """Get the absolute directions for each sensor"""
        directions = []
        for angle in self.sensor_angles:
            # Convert angle to direction index (45-degree increments)
            sensor_dir = (self.direction + angle // 45) % 8
            directions.append(sensor_dir)
        return directions
    
    def update_walls_from_sensors(self, sensor_data: List[int]):
        """Update wall map based on sensor readings"""
        sensor_dirs = self.get_sensor_directions()
        
        for i, (has_wall, sensor_dir) in enumerate(zip(sensor_data, sensor_dirs)):
            if has_wall:
                # There's a wall in this direction
                dx, dy = self.dir_vectors[sensor_dir]
                
                # Add wall between current cell and adjacent cell
                if sensor_dir in [0, 4]:  # North/South
                    if sensor_dir == 0:  # North wall
                        self.walls.add((self.x, self.y + 1, self.x + 1, self.y + 1))
                    else:  # South wall
                        self.walls.add((self.x, self.y, self.x + 1, self.y))
                elif sensor_dir in [2, 6]:  # East/West
                    if sensor_dir == 2:  # East wall
                        self.walls.add((self.x + 1, self.y, self.x + 1, self.y + 1))
                    else:  # West wall
                        self.walls.add((self.x, self.y, self.x, self.y + 1))
    
    def is_wall_between(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Check if there's a wall between two adjacent cells"""
        # Normalize the wall representation
        if x1 == x2:  # Vertical wall
            min_y, max_y = min(y1, y2), max(y1, y2)
            wall = (x1, max_y, x1 + 1, max_y) if max_y < self.maze_size else None
        else:  # Horizontal wall
            min_x, max_x = min(x1, x2), max(x1, x2)
            wall = (max_x, y1, max_x, y1 + 1) if max_x < self.maze_size else None
        
        return wall in self.walls if wall else True
    
    def get_valid_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighboring cells (no walls, within bounds)"""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Only cardinal directions
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.maze_size and 0 <= ny < self.maze_size and
                not self.is_wall_between(x, y, nx, ny)):
                neighbors.append((nx, ny))
        return neighbors
    
    def find_path_to_goal(self) -> List[Tuple[int, int]]:
        """Find shortest path to goal using A* algorithm"""
        def heuristic(pos):
            x, y = pos
            # Distance to nearest goal cell
            return min(abs(x - gx) + abs(y - gy) for gx, gy in self.goal_cells)
        
        start = (self.x, self.y)
        heap = [(0, 0, start, [start])]
        visited = set()
        
        while heap:
            f_cost, g_cost, (x, y), path = heapq.heappop(heap)
            
            if (x, y) in visited:
                continue
            visited.add((x, y))
            
            if (x, y) in self.goal_cells:
                return path
            
            for nx, ny in self.get_valid_neighbors(x, y):
                if (nx, ny) not in visited:
                    new_g_cost = g_cost + 1
                    new_f_cost = new_g_cost + heuristic((nx, ny))
                    new_path = path + [(nx, ny)]
                    heapq.heappush(heap, (new_f_cost, new_g_cost, (nx, ny), new_path))
        
        return []  # No path found
    
    def find_unexplored_cell(self) -> Optional[Tuple[int, int]]:
        """Find nearest unexplored cell using BFS"""
        queue = deque([(self.x, self.y, 0)])
        visited = {(self.x, self.y)}
        
        while queue:
            x, y, dist = queue.popleft()
            
            if (x, y) not in self.visited_cells:
                return (x, y)
            
            for nx, ny in self.get_valid_neighbors(x, y):
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny, dist + 1))
        
        return None  # All reachable cells explored
    
    def get_direction_to_target(self, target_x: int, target_y: int) -> int:
        """Get the direction (0-7) to face the target cell"""
        dx = target_x - self.x
        dy = target_y - self.y
        
        # Convert to direction index (only cardinal directions)
        if dx == 0 and dy == 1:
            return 0  # North
        elif dx == 1 and dy == 0:
            return 2  # East
        elif dx == 0 and dy == -1:
            return 4  # South
        elif dx == -1 and dy == 0:
            return 6  # West
        
        return self.direction  # Keep current direction if unclear
    
    def calculate_turn_moves(self, target_direction: int) -> List[str]:
        """Calculate the moves needed to turn to target direction"""
        moves = []
        current_dir = self.direction
        
        # Only allow cardinal directions for movement
        if target_direction not in [0, 2, 4, 6]:
            return moves
        
        while current_dir != target_direction:
            # Calculate shortest rotation (in 45-degree increments)
            diff = (target_direction - current_dir) % 8
            if diff <= 4:
                moves.append('R')  # Turn right (clockwise)
                current_dir = (current_dir + 1) % 8
            else:
                moves.append('L')  # Turn left (counter-clockwise)
                current_dir = (current_dir - 1) % 8
        
        return moves
    
    def generate_movement_instructions(self, target_x: int, target_y: int) -> List[str]:
        """Generate movement instructions to reach target cell"""
        instructions = []
        
        # First, turn to face the target (only if we need to move)
        if target_x != self.x or target_y != self.y:
            target_direction = self.get_direction_to_target(target_x, target_y)
            if target_direction != self.direction:
                turn_moves = self.calculate_turn_moves(target_direction)
                instructions.extend(turn_moves)
                self.direction = target_direction
        
        # Then move forward if we're facing the right direction
        if self.momentum == 0:
            instructions.append('F2')  # Accelerate from rest
        elif self.momentum > 0:
            instructions.append('F1')  # Maintain forward speed
        else:
            instructions.append('BB')  # Brake if going backward
        
        return instructions
    
    def generate_instructions(self, game_data: dict) -> List[str]:
        """Main logic to generate movement instructions"""
        # Update mouse state
        self.momentum = game_data['momentum']
        sensor_data = game_data['sensor_data']
        
        # Update wall knowledge
        self.update_walls_from_sensors(sensor_data)
        self.visited_cells.add((self.x, self.y))
        
        logger.info(f"Mouse at ({self.x}, {self.y}), direction: {self.direction}, momentum: {self.momentum}")
        logger.info(f"Sensor data: {sensor_data}")
        
        # If we've reached the goal, stop
        if game_data['goal_reached']:
            logger.info("Goal reached! Stopping.")
            return ['BB'] if self.momentum != 0 else []
        
        # Strategy: Explore first, then find optimal path
        if self.exploration_phase:
            # Switch to optimization phase after exploring enough or running out of time
            if len(self.visited_cells) > 50 or game_data['total_time_ms'] > 200000:
                logger.info("Switching to optimization phase")
                self.exploration_phase = False
                self.path_to_goal = self.find_path_to_goal()
                self.current_path_index = 1  # Skip current position
        
        if not self.exploration_phase and self.path_to_goal:
            # Follow the planned path to goal
            if self.current_path_index < len(self.path_to_goal):
                target_x, target_y = self.path_to_goal[self.current_path_index]
                logger.info(f"Following path to goal: target ({target_x}, {target_y})")
                instructions = self.generate_movement_instructions(target_x, target_y)
                
                # Update position after successful movement
                if instructions and any(move in instructions for move in ['F1', 'F2']):
                    self.x, self.y = target_x, target_y
                    self.current_path_index += 1
                
                return instructions
        else:
            # Exploration phase - find unexplored areas
            unexplored = self.find_unexplored_cell()
            if unexplored:
                target_x, target_y = unexplored
                logger.info(f"Exploring: target ({target_x}, {target_y})")
                instructions = self.generate_movement_instructions(target_x, target_y)
                
                # Update position after successful movement
                if instructions and any(move in instructions for move in ['F1', 'F2']):
                    self.x, self.y = target_x, target_y
                
                return instructions
            else:
                # All explored, find path to goal
                logger.info("All accessible cells explored, finding path to goal")
                self.path_to_goal = self.find_path_to_goal()
                if self.path_to_goal and len(self.path_to_goal) > 1:
                    target_x, target_y = self.path_to_goal[1]
                    return self.generate_movement_instructions(target_x, target_y)
        
        # Default: stop or brake safely
        logger.info("No valid move found, braking")
        return ['BB'] if self.momentum != 0 else []

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
