import json
import logging
from flask import request
from routes import app
from collections import deque

logger = logging.getLogger(__name__)

class FloodFillMicroMouse:
    def __init__(self):
        # Maze setup
        self.maze_size = 16
        self.goal_cells = [(7, 7), (7, 8), (8, 7), (8, 8)]
        
        # Initialize flood values - distance to goal
        self.flood_values = [[0 for _ in range(16)] for _ in range(16)]
        
        # Wall representation: walls[x][y] = {'N': bool, 'E': bool, 'S': bool, 'W': bool}
        self.walls = {}
        for x in range(16):
            for y in range(16):
                self.walls[(x, y)] = {'N': False, 'E': False, 'S': False, 'W': False}
        
        # Add perimeter walls
        for i in range(16):
            self.walls[(i, 0)]['S'] = True
            self.walls[(i, 15)]['N'] = True
            self.walls[(0, i)]['W'] = True
            self.walls[(15, i)]['E'] = True
        
        # Mouse state
        self.x, self.y = 0, 0  # Position
        self.direction = 'N'  # N, E, S, W
        self.momentum = 0
        
        # Strategy
        self.phase = 'explore'  # 'explore' or 'speed_run'
        self.visited = set()
        self.path = []
        self.game_uuid = None
        
        # Initialize flood fill
        self.calculate_flood_fill()
        
        # Direction mappings
        self.dir_map = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
        self.opposite = {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'}
        self.left_turn = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}
        self.right_turn = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}
        
    def reset_for_new_game(self, game_uuid):
        if self.game_uuid != game_uuid:
            self.__init__()
            self.game_uuid = game_uuid
            logger.info(f"Reset for new game: {game_uuid}")
    
    def calculate_flood_fill(self):
        """Calculate flood fill values from goal cells"""
        # Reset all values to max
        for x in range(16):
            for y in range(16):
                self.flood_values[x][y] = 255
        
        # Initialize goal cells
        queue = deque()
        for gx, gy in self.goal_cells:
            self.flood_values[gx][gy] = 0
            queue.append((gx, gy, 0))
        
        # Flood fill
        while queue:
            x, y, distance = queue.popleft()
            
            # Check all 4 directions
            for direction, (dx, dy) in [('N', (0, 1)), ('E', (1, 0)), ('S', (0, -1)), ('W', (-1, 0))]:
                nx, ny = x + dx, y + dy
                
                # Check bounds
                if 0 <= nx < 16 and 0 <= ny < 16:
                    # Check if there's a wall blocking this direction
                    if not self.walls[(x, y)][direction]:
                        new_distance = distance + 1
                        if new_distance < self.flood_values[nx][ny]:
                            self.flood_values[nx][ny] = new_distance
                            queue.append((nx, ny, new_distance))
    
    def update_walls_from_sensors(self, sensor_data):
        """Update walls based on sensor readings"""
        # Sensor positions: [-90°, -45°, 0°, 45°, 90°] relative to heading
        directions_map = {
            'N': ['W', 'W', 'N', 'E', 'E'],  # When facing North
            'E': ['N', 'N', 'E', 'S', 'S'],  # When facing East  
            'S': ['E', 'E', 'S', 'W', 'W'],  # When facing South
            'W': ['S', 'S', 'W', 'N', 'N']   # When facing West
        }
        
        sensor_dirs = directions_map[self.direction]
        
        # Update walls based on sensor readings
        for i, has_wall in enumerate(sensor_data):
            if has_wall == 1:  # Wall detected
                wall_direction = sensor_dirs[i]
                self.walls[(self.x, self.y)][wall_direction] = True
                
                # Also update adjacent cell
                dx, dy = {'N': (0, 1), 'E': (1, 0), 'S': (0, -1), 'W': (-1, 0)}[wall_direction]
                adj_x, adj_y = self.x + dx, self.y + dy
                if 0 <= adj_x < 16 and 0 <= adj_y < 16:
                    self.walls[(adj_x, adj_y)][self.opposite[wall_direction]] = True
        
        # Mark cell as visited
        self.visited.add((self.x, self.y))
    
    def get_accessible_neighbors(self, x, y):
        """Get neighboring cells that are accessible (no walls)"""
        neighbors = []
        for direction, (dx, dy) in [('N', (0, 1)), ('E', (1, 0)), ('S', (0, -1)), ('W', (-1, 0))]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 16 and 0 <= ny < 16 and not self.walls[(x, y)][direction]:
                neighbors.append((nx, ny, direction))
        return neighbors
    
    def find_next_move_flood_fill(self):
        """Find next move using flood fill algorithm"""
        current_value = self.flood_values[self.x][self.y]
        
        # Find the neighboring cell with lowest flood value
        neighbors = self.get_accessible_neighbors(self.x, self.y)
        if not neighbors:
            return None
        
        best_neighbor = min(neighbors, key=lambda n: self.flood_values[n[0]][n[1]])
        target_x, target_y, move_direction = best_neighbor
        
        # If current cell has higher value than neighbor, move there
        if self.flood_values[target_x][target_y] < current_value:
            return move_direction
        
        # If stuck, recalculate flood fill and try again
        self.calculate_flood_fill()
        neighbors = self.get_accessible_neighbors(self.x, self.y)
        if neighbors:
            best_neighbor = min(neighbors, key=lambda n: self.flood_values[n[0]][n[1]])
            return best_neighbor[2]
        
        return None
    
    def calculate_turns_needed(self, target_direction):
        """Calculate number of turns needed to face target direction"""
        if self.direction == target_direction:
            return 0
        elif self.right_turn[self.direction] == target_direction:
            return 1  # Right turn
        elif self.left_turn[self.direction] == target_direction:
            return -1  # Left turn
        else:
            return 2  # U-turn
    
    def generate_movement_instructions(self, target_direction):
        """Generate movement instructions to face and move in target direction"""
        instructions = []
        
        # Calculate turns needed
        turns_needed = self.calculate_turns_needed(target_direction)
        
        if turns_needed == 1:  # Right turn
            instructions.append('R')
            self.direction = self.right_turn[self.direction]
        elif turns_needed == -1:  # Left turn
            instructions.append('L')
            self.direction = self.left_turn[self.direction]
        elif turns_needed == 2:  # U-turn
            instructions.extend(['R', 'R'])
            self.direction = self.opposite[self.direction]
        
        # Move forward
        if self.momentum == 0:
            instructions.append('F2')  # Accelerate
        else:
            instructions.append('F1')  # Maintain speed
        
        # Update position
        dx, dy = {'N': (0, 1), 'E': (1, 0), 'S': (0, -1), 'W': (-1, 0)}[target_direction]
        self.x += dx
        self.y += dy
        
        return instructions
    
    def solve(self, game_data):
        """Main solving logic"""
        self.momentum = game_data['momentum']
        sensor_data = game_data['sensor_data']
        goal_reached = game_data['goal_reached']
        
        logger.info(f"Position: ({self.x}, {self.y}), Direction: {self.direction}, Momentum: {self.momentum}")
        logger.info(f"Sensors: {sensor_data}, Goal: {goal_reached}")
        
        # If goal reached, stop
        if goal_reached:
            if self.phase == 'explore':
                logger.info("Goal reached in exploration phase!")
                self.phase = 'speed_run'
                # Reset position for speed run
                self.x, self.y = 0, 0
                self.direction = 'N'
                return ['BB'] if self.momentum != 0 else []
            else:
                logger.info("Goal reached in speed run!")
                return []
        
        # Update wall knowledge from sensors
        self.update_walls_from_sensors(sensor_data)
        
        # Recalculate flood fill with new wall information
        self.calculate_flood_fill()
        
        # If we have momentum, handle it carefully
        if self.momentum != 0:
            # Check if we can continue in current direction
            front_sensor = sensor_data[2]  # Front sensor
            if front_sensor == 1:  # Wall ahead
                return ['BB']  # Brake
            else:
                return ['F1']  # Continue
        
        # At rest - decide next move using flood fill
        next_direction = self.find_next_move_flood_fill()
        
        if next_direction:
            instructions = self.generate_movement_instructions(next_direction)
            logger.info(f"Moving {next_direction}, instructions: {instructions}")
            return instructions
        else:
            logger.info("No valid move found")
            return []

# Global solver instance
solver = FloodFillMicroMouse()

@app.route('/micro-mouse', methods=['POST'])
def micromouse():
    try:
        data = request.get_json()
        logger.info("Micromouse request: {}".format(data))
        
        # Reset for new games
        game_uuid = data.get('game_uuid')
        solver.reset_for_new_game(game_uuid)
        
        # Get instructions from solver
        instructions = solver.solve(data)
        
        result = {
            "instructions": instructions,
            "end": False
        }
        
        logger.info("Response: {}".format(result))
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Error in micromouse: {str(e)}")
        return json.dumps({
            "instructions": ["BB"],
            "end": False
        })
