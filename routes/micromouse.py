import json
import requests
from collections import deque, defaultdict
import heapq
from typing import List, Tuple, Optional, Dict, Set

class MicroMouseSolver:
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        
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
                wall_x = self.x + dx
                wall_y = self.y + dy
                
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
            wall = (x1, max_y, x1 + 1, max_y) if x1 < self.maze_size - 1 else None
        else:  # Horizontal wall
            min_x, max_x = min(x1, x2), max(x1, x2)
            wall = (max_x, y1, max_x, y1 + 1) if y1 < self.maze_size - 1 else None
        
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
        
        # Convert to direction index
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
        
        while current_dir != target_direction:
            # Calculate shortest rotation
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
        
        # First, turn to face the target
        target_direction = self.get_direction_to_target(target_x, target_y)
        turn_moves = self.calculate_turn_moves(target_direction)
        instructions.extend(turn_moves)
        
        # Then move forward
        if self.momentum == 0:
            instructions.append('F2')  # Accelerate
        else:
            instructions.append('F1')  # Maintain speed
        
        return instructions
    
    def generate_instructions(self, game_data: dict) -> List[str]:
        """Main logic to generate movement instructions"""
        # Update mouse state
        self.momentum = game_data['momentum']
        sensor_data = game_data['sensor_data']
        
        # Update wall knowledge
        self.update_walls_from_sensors(sensor_data)
        self.visited_cells.add((self.x, self.y))
        
        # If we've reached the goal, stop
        if game_data['goal_reached']:
            return ['BB'] if self.momentum != 0 else []
        
        # Strategy: Explore first, then find optimal path
        if self.exploration_phase:
            # Check if we have a good understanding of the maze
            if len(self.visited_cells) > 50 or game_data['total_time_ms'] > 200000:
                self.exploration_phase = False
                self.path_to_goal = self.find_path_to_goal()
                self.current_path_index = 1  # Skip current position
        
        if not self.exploration_phase and self.path_to_goal:
            # Follow the planned path to goal
            if self.current_path_index < len(self.path_to_goal):
                target_x, target_y = self.path_to_goal[self.current_path_index]
                instructions = self.generate_movement_instructions(target_x, target_y)
                
                # Update position (simplified - assumes we move one cell per instruction batch)
                if instructions and any(move in instructions for move in ['F1', 'F2']):
                    self.x, self.y = target_x, target_y
                    self.current_path_index += 1
                
                return instructions
        else:
            # Exploration phase - find unexplored areas
            unexplored = self.find_unexplored_cell()
            if unexplored:
                target_x, target_y = unexplored
                instructions = self.generate_movement_instructions(target_x, target_y)
                
                # Update position
                if instructions and any(move in instructions for move in ['F1', 'F2']):
                    self.x, self.y = target_x, target_y
                
                return instructions
            else:
                # All explored, find path to goal
                self.path_to_goal = self.find_path_to_goal()
                if self.path_to_goal and len(self.path_to_goal) > 1:
                    target_x, target_y = self.path_to_goal[1]
                    return self.generate_movement_instructions(target_x, target_y)
        
        # Default: move forward or brake
        if self.momentum > 0:
            return ['BB']  # Brake if moving
        else:
            return ['F2']  # Try to move forward
    
    def solve(self, game_data: dict) -> dict:
        """Main solver method"""
        instructions = self.generate_instructions(game_data)
        
        return {
            "instructions": instructions,
            "end": False
        }


def main():
    """Example usage"""
    # Initialize solver with your endpoint URL
    solver = MicroMouseSolver("http://your-endpoint-url/micro-mouse")
    
    # Example game data (you would receive this from the API)
    game_data = {
        "game_uuid": "uharhtrfunp6",
        "sensor_data": [1, 1, 0, 0, 0],
        "is_crashed": False,
        "total_time_ms": 0,
        "goal_reached": False,
        "best_time_ms": None,
        "run_time_ms": 0,
        "run": 0,
        "momentum": 0
    }
    
    # Get instructions
    response = solver.solve(game_data)
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()


# Usage example for HTTP requests:
"""
import requests

def run_micromouse_solver():
    solver = MicroMouseSolver("http://localhost:8000/micro-mouse")
    
    # Game loop
    while True:
        # Get current game state (this would come from your game server)
        game_data = get_game_state()  # You need to implement this
        
        # Generate response
        response = solver.solve(game_data)
        
        # Send response to server
        result = requests.post("http://localhost:8000/micro-mouse", json=response)
        
        # Check if game ended
        if response.get("end", False) or game_data.get("is_crashed", False):
            break
        
        # Update solver state based on result
        # (You may need to update mouse position based on server response)
"""
