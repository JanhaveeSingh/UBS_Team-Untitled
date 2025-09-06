import json
import logging
import math
from collections import deque
from typing import List, Tuple, Dict, Set, Optional

from flask import request

from routes import app

logger = logging.getLogger(__name__)

# Global state to track the micromouse progress
mouse_state = {
    'x': 0,
    'y': 0,
    'direction': 0,  # 0: North, 1: East, 2: South, 3: West
    'momentum': 0,
    'maze': [[0 for _ in range(16)] for _ in range(16)],  # 0: unknown, 1: open, 2: wall
    'visited': set(),
    'goal_cells': [(7, 7), (7, 8), (8, 7), (8, 8)],  # Center 2x2 goal area
    'path': [],
    'exploration_mode': True,
    'best_path': [],
    'run_count': 0
}

@app.route('/micro-mouse', methods=['POST'])
def micromouse():
    data = request.get_json()
    logging.info("MicroMouse data received: {}".format(data))
    
    # Update mouse state from request
    game_uuid = data.get("game_uuid")
    sensor_data = data.get("sensor_data", [])
    total_time_ms = data.get("total_time_ms", 0)
    goal_reached = data.get("goal_reached", False)
    best_time_ms = data.get("best_time_ms")
    run_time_ms = data.get("run_time_ms", 0)
    run = data.get("run", 0)
    momentum = data.get("momentum", 0)
    
    # Update global state
    mouse_state['momentum'] = momentum
    
    # If this is a new run, reset position
    if run > mouse_state['run_count']:
        mouse_state['x'] = 0
        mouse_state['y'] = 0
        mouse_state['direction'] = 0
        mouse_state['run_count'] = run
        if run > 1 and not goal_reached:
            mouse_state['exploration_mode'] = False  # Switch to optimized path after first run
    
    # Process sensor data to update maze knowledge
    process_sensor_data(sensor_data)
    
    # Determine next moves
    if goal_reached:
        instructions = []
        end = True
    else:
        if mouse_state['exploration_mode']:
            instructions = explore_maze()
            end = False
        else:
            instructions = follow_optimized_path()
            end = False
    
    response = {
        "instructions": instructions,
        "end": end
    }
    
    logging.info("MicroMouse response: {}".format(response))
    return json.dumps(response)

def process_sensor_data(sensor_data: List[int]):
    """Update maze knowledge based on sensor readings"""
    x, y = mouse_state['x'], mouse_state['y']
    direction = mouse_state['direction']
    
    # Mark current cell as visited
    mouse_state['visited'].add((x, y))
    mouse_state['maze'][y][x] = 1  # Mark as open
    
    # Sensor angles: -90°, -45°, 0°, +45°, +90° relative to current direction
    # Range up to 12 cm (about 0.75 cells)
    
    # Process each sensor reading
    for i, distance in enumerate(sensor_data):
        sensor_angle = i * 45 - 90  # Convert index to angle
        
        # Calculate absolute direction
        abs_direction = (direction + round(sensor_angle / 45)) % 4
        
        # Calculate cell coordinates in sensor direction
        if abs_direction == 0:  # North
            dx, dy = 0, 1
        elif abs_direction == 1:  # East
            dx, dy = 1, 0
        elif abs_direction == 2:  # South
            dx, dy = 0, -1
        else:  # West
            dx, dy = -1, 0
        
        # If sensor detects no wall, mark cell as open
        if distance == 1:  # Assuming 1 means no wall detected
            nx, ny = x + dx, y + dy
            if 0 <= nx < 16 and 0 <= ny < 16:
                mouse_state['maze'][ny][nx] = 1
        else:  # Wall detected
            nx, ny = x + dx, y + dy
            if 0 <= nx < 16 and 0 <= ny < 16:
                mouse_state['maze'][ny][nx] = 2

def explore_maze() -> List[str]:
    """Explore the maze using a wall-following algorithm"""
    x, y = mouse_state['x'], mouse_state['y']
    direction = mouse_state['direction']
    
    # If we're in the goal area, try to stop
    if (x, y) in mouse_state['goal_cells'] and mouse_state['momentum'] == 0:
        return []
    
    # Try to prioritize right-hand wall following
    directions_to_try = [
        (direction + 1) % 4,  # Right
        direction,             # Forward
        (direction + 3) % 4,  # Left
        (direction + 2) % 4,  # Back
    ]
    
    for next_dir in directions_to_try:
        dx, dy = get_direction_vector(next_dir)
        nx, ny = x + dx, y + dy
        
        # Check if the cell is within bounds and not a wall
        if 0 <= nx < 16 and 0 <= ny < 16 and mouse_state['maze'][ny][nx] != 2:
            # Calculate turns needed
            turns = (next_dir - direction) % 4
            if turns == 3:  # Equivalent to -1 (left turn)
                turns = -1
            
            # Generate instructions based on current momentum and required turns
            return generate_movement_instructions(turns, 1)  # Move one cell
    
    # If all directions are blocked, turn around
    return generate_movement_instructions(2, 0)  # 180 degree turn

def follow_optimized_path() -> List[str]:
    """Follow the optimized path to the goal"""
    x, y = mouse_state['x'], mouse_state['y']
    
    # If we're in the goal area, try to stop
    if (x, y) in mouse_state['goal_cells'] and mouse_state['momentum'] == 0:
        return []
    
    # If we don't have a path or we've deviated, calculate a new path
    if not mouse_state['path'] or (x, y) != mouse_state['path'][0]:
        mouse_state['path'] = find_shortest_path((x, y), mouse_state['goal_cells'])
    
    if not mouse_state['path']:
        # Fall back to exploration if no path found
        return explore_maze()
    
    # Get next cell in path
    next_cell = mouse_state['path'][0]
    dx = next_cell[0] - x
    dy = next_cell[1] - y
    
    # Determine required direction
    if dx == 1: next_dir = 1  # East
    elif dx == -1: next_dir = 3  # West
    elif dy == 1: next_dir = 0  # North
    else: next_dir = 2  # South
    
    # Calculate turns needed
    turns = (next_dir - mouse_state['direction']) % 4
    if turns == 3:  # Equivalent to -1 (left turn)
        turns = -1
    
    # Remove the current cell from path
    mouse_state['path'] = mouse_state['path'][1:]
    
    return generate_movement_instructions(turns, 1)

def find_shortest_path(start: Tuple[int, int], goals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Find the shortest path from start to any goal cell using BFS"""
    queue = deque([(start, [])])
    visited = set([start])
    
    while queue:
        (x, y), path = queue.popleft()
        
        # Check if we've reached a goal
        if (x, y) in goals:
            return path + [(x, y)]
        
        # Try all four directions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            
            # Check if the cell is valid and traversable
            if (0 <= nx < 16 and 0 <= ny < 16 and 
                mouse_state['maze'][ny][nx] == 1 and 
                (nx, ny) not in visited):
                
                queue.append(((nx, ny), path + [(x, y)]))
                visited.add((nx, ny))
    
    return []  # No path found

def get_direction_vector(direction: int) -> Tuple[int, int]:
    """Convert direction index to dx, dy vector"""
    if direction == 0:  # North
        return (0, 1)
    elif direction == 1:  # East
        return (1, 0)
    elif direction == 2:  # South
        return (0, -1)
    else:  # West
        return (-1, 0)

def generate_movement_instructions(turns: int, cells: int) -> List[str]:
    """Generate movement instructions based on required turns and cells to move"""
    instructions = []
    direction = mouse_state['direction']
    momentum = mouse_state['momentum']
    
    # Handle turns
    if turns == 1:  # Right turn (90°)
        if momentum == 0:
            instructions.extend(['R', 'R'])  # Two 45° turns
        else:
            instructions.append('BBR')  # Brake and turn right
    elif turns == -1:  # Left turn (90°)
        if momentum == 0:
            instructions.extend(['L', 'L'])  # Two 45° turns
        else:
            instructions.append('BBL')  # Brake and turn left
    elif turns == 2:  # 180° turn
        if momentum == 0:
            instructions.extend(['R', 'R', 'R', 'R'])  # Four 45° turns
        else:
            instructions.extend(['BB', 'R', 'R'])  # Brake and turn around
    
    # Update direction after turns
    new_direction = (direction + turns) % 4
    mouse_state['direction'] = new_direction
    
    # Handle forward movement
    if cells > 0:
        if momentum == 0:
            # Accelerate from stop
            instructions.extend(['F2'] * min(cells, 4))
        elif momentum > 0:
            # Maintain or adjust speed
            instructions.extend(['F1'] * cells)
        else:
            # Need to stop and change direction
            instructions.append('BB')
            instructions.extend(['F2'] * cells)
    
    return instructions
