"""
2048 Game Server Implementation
Handles the game logic for the 2048 puzzle game.
"""

import json
import random
import logging
from typing import List, Optional, Tuple, Dict, Any
from flask import request, jsonify

from routes import app

logger = logging.getLogger(__name__)

class Game2048:
    """2048 game logic implementation"""
    
    def __init__(self):
        pass  # Remove grid_size constraint
        
    def is_valid_grid(self, grid: List[List]) -> bool:
        """Validate that the grid is NxN with valid values"""
        if not isinstance(grid, list) or len(grid) == 0:
            return False
        
        grid_size = len(grid)
        for row in grid:
            if not isinstance(row, list) or len(row) != grid_size:
                return False
            for cell in row:
                if cell is not None and not self.is_valid_cell_value(cell):
                    return False
        return True
    
    def is_valid_cell_value(self, cell) -> bool:
        """Check if a cell value is valid"""
        if cell is None:
            return True
        
        # Handle special tiles
        if cell == 0 or cell == '0':
            return True
        if cell == '*2':
            return True
        if cell == 1 or cell == '1':
            return True
            
        # Handle regular number tiles (must be power of 2 and >= 2)
        if isinstance(cell, int) and cell >= 2 and (cell & (cell - 1)) == 0:
            return True
            
        return False
    
    def add_random_tile(self, grid: List[List]) -> List[List]:
        """Add a random tile (2 or 4) to an empty cell"""
        grid_size = len(grid)
        
        # Find empty cells
        empty_cells = []
        for r in range(grid_size):
            for c in range(grid_size):
                if grid[r][c] is None:
                    empty_cells.append((r, c))
        
        if not empty_cells:
            return grid  # No empty cells
        
        # Choose random empty cell
        r, c = random.choice(empty_cells)
        
        # 90% chance for 2, 10% chance for 4
        grid[r][c] = 2 if random.random() < 0.9 else 4
        
        return grid
    
    def move_left(self, grid: List[List]) -> Tuple[List[List], bool]:
        """Move and merge tiles to the left, return (new_grid, changed)"""
        grid_size = len(grid)
        new_grid = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        changed = False
        
        for r in range(grid_size):
            # Process each row
            row = grid[r][:]
            new_row = self.process_row_left(row)
            
            for c in range(grid_size):
                new_grid[r][c] = new_row[c]
                if new_grid[r][c] != grid[r][c]:
                    changed = True
        
        return new_grid, changed
    
    def process_row_left(self, row: List) -> List:
        """Process a single row moving left with all special tile rules"""
        result = [None] * len(row)
        
        # Handle '0' tiles which don't move and create barriers
        result_pos = 0
        i = 0
        
        while i < len(row):
            if row[i] == 0 or row[i] == '0':
                # '0' stays exactly where it is
                result[i] = row[i]
                
                # Process everything to the left of this '0'
                left_part = row[:i]
                if left_part:
                    processed_left = self.process_segment_left(left_part)
                    for j, val in enumerate(processed_left):
                        if j < i:
                            result[j] = val
                
                # Process everything to the right of this '0' recursively
                right_part = row[i+1:]
                if right_part:
                    processed_right = self.process_row_left(right_part)
                    for j, val in enumerate(processed_right):
                        if i + 1 + j < len(result):
                            result[i + 1 + j] = val
                
                return result
            i += 1
        
        # No '0' tiles found, process normally
        processed = self.process_segment_left(row)
        for i, val in enumerate(processed):
            if i < len(result):
                result[i] = val
        
        return result
    
    def process_segment_left(self, segment: List) -> List:
        """Process a segment without '0' tiles"""
        # Remove None values first
        non_none = [cell for cell in segment if cell is not None]
        if not non_none:
            return []
        
        # Handle special tile interactions in order
        # 1. First, process '1' + '*2' conversions (immediate adjacency only)
        processed = []
        skip_next = False
        converted_positions = set()  # Track which positions had '1' -> '2' conversions
        
        for i in range(len(non_none)):
            if skip_next:
                skip_next = False
                continue
                
            cell = non_none[i]
            
            if (cell == 1 or cell == '1') and i + 1 < len(non_none) and non_none[i + 1] == '*2':
                # '1' followed by '*2' -> convert '1' to '2' and consume the '*2'
                processed.append(2)
                converted_positions.add(len(processed) - 1)  # Mark this position as converted
                skip_next = True  # Skip the '*2' as it's consumed
            else:
                processed.append(cell)
        
        # 2. Now handle regular movement and '*2' multiplication
        result = []
        for i, cell in enumerate(processed):
            if cell == '*2':
                # '*2' multiplies the previous number if it exists, 
                # but NOT if it was just converted from '1'
                if (result and isinstance(result[-1], int) and result[-1] >= 1 and
                    (len(result) - 1) not in converted_positions):
                    result[-1] = result[-1] * 2
                result.append('*2')
            else:
                # Regular number - check for normal merging
                if (result and 
                    result[-1] == cell and 
                    isinstance(cell, int) and 
                    cell >= 2):
                    result[-1] = cell * 2
                else:
                    result.append(cell)
        
        # 3. Handle special '*2' compression patterns
        return self.final_times2_compression(result)
    
    def final_times2_compression(self, tiles: List) -> List:
        """Handle final '*2' compression based on the exact example pattern"""
        if len(tiles) < 2:
            return tiles
            
        # Look for pattern: [..., '*2', number] at the end
        # If found, one of the preceding '*2' tiles should merge with that number
        if (len(tiles) >= 2 and 
            isinstance(tiles[-1], int) and 
            tiles[-2] == '*2'):
            
            # Count consecutive '*2' tiles before the final number
            times2_count = 0
            for i in range(len(tiles) - 2, -1, -1):
                if tiles[i] == '*2':
                    times2_count += 1
                else:
                    break
            
            # If we have multiple '*2' tiles before a number, 
            # remove one '*2' (it merges with the number, but number stays same per example)
            if times2_count > 1:
                # Remove one '*2' from the sequence
                result = tiles[:]
                for i in range(len(result) - 2, -1, -1):
                    if result[i] == '*2':
                        result.pop(i)
                        break
                return result
        
        return tiles
    
    def move_right(self, grid: List[List]) -> Tuple[List[List], bool]:
        """Move and merge tiles to the right"""
        # Reverse each row, move left, then reverse back
        reversed_grid = [row[::-1] for row in grid]
        moved_grid, changed = self.move_left(reversed_grid)
        result_grid = [row[::-1] for row in moved_grid]
        return result_grid, changed
    
    def move_up(self, grid: List[List]) -> Tuple[List[List], bool]:
        """Move and merge tiles upward"""
        grid_size = len(grid)
        # Transpose, move left, then transpose back
        transposed = [[grid[r][c] for r in range(grid_size)] for c in range(grid_size)]
        moved_transposed, changed = self.move_left(transposed)
        result_grid = [[moved_transposed[c][r] for c in range(grid_size)] for r in range(grid_size)]
        return result_grid, changed
    
    def move_down(self, grid: List[List]) -> Tuple[List[List], bool]:
        """Move and merge tiles downward"""
        grid_size = len(grid)
        # Transpose, move right, then transpose back
        transposed = [[grid[r][c] for r in range(grid_size)] for c in range(grid_size)]
        moved_transposed, changed = self.move_right(transposed)
        result_grid = [[moved_transposed[c][r] for c in range(grid_size)] for r in range(grid_size)]
        return result_grid, changed
    
    def make_move(self, grid: List[List], direction: str) -> Tuple[List[List], bool]:
        """Make a move in the specified direction"""
        direction = direction.upper()
        
        if direction == "LEFT":
            return self.move_left(grid)
        elif direction == "RIGHT":
            return self.move_right(grid)
        elif direction == "UP":
            return self.move_up(grid)
        elif direction == "DOWN":
            return self.move_down(grid)
        else:
            raise ValueError(f"Invalid direction: {direction}")
    
    def check_win(self, grid: List[List]) -> bool:
        """Check if the player has won (reached 2048)"""
        for row in grid:
            for cell in row:
                if isinstance(cell, int) and cell >= 2048:
                    return True
        return False
    
    def can_move(self, grid: List[List]) -> bool:
        """Check if any moves are possible"""
        grid_size = len(grid)
        
        # Check for empty cells
        for row in grid:
            if None in row:
                return True
        
        # Check for possible merges horizontally
        for r in range(grid_size):
            for c in range(grid_size - 1):
                cell1, cell2 = grid[r][c], grid[r][c + 1]
                if self.can_merge(cell1, cell2):
                    return True
        
        # Check for possible merges vertically
        for r in range(grid_size - 1):
            for c in range(grid_size):
                cell1, cell2 = grid[r][c], grid[r + 1][c]
                if self.can_merge(cell1, cell2):
                    return True
        
        return False
    
    def can_merge(self, cell1, cell2) -> bool:
        """Check if two cells can merge"""
        if cell1 is None or cell2 is None:
            return False
        
        # Regular numbers can merge if they're equal and >= 2
        if (isinstance(cell1, int) and isinstance(cell2, int) and 
            cell1 == cell2 and cell1 >= 2):
            return True
            
        # '*2' can merge with numbers
        if cell1 == '*2' and isinstance(cell2, int) and cell2 >= 1:
            return True
        if cell2 == '*2' and isinstance(cell1, int) and cell1 >= 1:
            return True
            
        return False
    
    def process_move(self, grid: List[List], direction: str) -> Dict[str, Any]:
        """Process a move and return the result"""
        try:
            # Validate input
            if not self.is_valid_grid(grid):
                return {
                    "nextGrid": grid,
                    "endGame": None,
                    "error": "Invalid grid format"
                }
            
            # Make the move
            new_grid, changed = self.make_move(grid, direction)
            
            # If nothing changed, return the original grid
            if not changed:
                return {
                    "nextGrid": grid,
                    "endGame": None
                }
            
            # Add a new random tile
            new_grid = self.add_random_tile(new_grid)
            
            # Check win condition
            if self.check_win(new_grid):
                return {
                    "nextGrid": new_grid,
                    "endGame": "win"
                }
            
            # Check lose condition
            if not self.can_move(new_grid):
                return {
                    "nextGrid": new_grid,
                    "endGame": "lose"
                }
            
            # Game continues
            return {
                "nextGrid": new_grid,
                "endGame": None
            }
            
        except Exception as e:
            logger.error(f"Error processing move: {e}")
            return {
                "nextGrid": grid,
                "endGame": None,
                "error": str(e)
            }

# Global game instance
game_2048 = Game2048()

@app.route('/2048', methods=['POST', 'OPTIONS'])
def game_2048_endpoint():
    """
    2048 game endpoint
    Expected input: {"grid": 4x4 array, "mergeDirection": "UP"/"DOWN"/"LEFT"/"RIGHT"}
    Returns: {"nextGrid": 4x4 array, "endGame": null/"win"/"lose"}
    """
    # Handle preflight CORS request
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    try:
        # Parse request
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        grid = data.get('grid')
        merge_direction = data.get('mergeDirection')
        
        if not grid:
            return jsonify({"error": "Missing 'grid' field"}), 400
        
        if not merge_direction:
            return jsonify({"error": "Missing 'mergeDirection' field"}), 400
        
        logger.info(f"2048 move: direction={merge_direction}")
        logger.debug(f"Current grid: {grid}")
        
        # Process the move
        result = game_2048.process_move(grid, merge_direction)
        
        logger.debug(f"Result grid: {result.get('nextGrid')}")
        logger.info(f"End game status: {result.get('endGame')}")
        
        # Add CORS headers to response
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"Error in 2048 endpoint: {e}")
        response = jsonify({"error": "Internal server error"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/2048.html', methods=['GET'])
def serve_2048_html():
    """Serve the 2048 HTML file for testing"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <title>2048</title>
    <style>
        body {
            font-family: Arial, Helvetica, sans-serif;
            background: #f0f4f8;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0;
            padding: 0;
        }

        h1 {
            margin: 20px 0 10px 0;
            color: #333;
        }

        svg {
            width: 420px;
            height: 420px;
            background: #fff;
            border: 1px solid #ddd;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        rect {
            stroke: #bbb;
            stroke-width: 1;
        }

        rect:hover {
            stroke: #777;
            fill: #777;
        }

        text {
            font-size: 30px;
            fill: #333;
            text-anchor: middle;
            dominant-baseline: central;
        }

        .input-holder {
            display: flex;
            align-items: baseline;
            margin: 8px;
        }

        input#server-url {
            field-sizing: content;
            min-width: 150px;
        }
    </style>
</head>
<body>
<h1>2048</h1>
<div class="input-holder">
    <div>
        Logic URL:
    </div>
    <div>
        <input id="server-url" placeholder="https://your-challenge-server-url" value="https://ubs-team-untitled.onrender.com">
    </div>
    <div>
        /2048
    </div>
</div>
<svg viewBox="0 0 400 400" id="gridSvg"></svg>
<p id="endGameText"></p>

<script>
    function getEndGameMessage(endGame) {
        switch(endGame) {
            case 'win':
                return 'You WIN! Congratulations!'
            case 'lose':
                return 'You LOSE! Press F5 to try again!'
            case null:
                return ''
            default:
                throw new Error(`Unknown Endgame status ${endGame}`)
        }
    }
    function renderGrid(grid) {
        const svg = document.getElementById("gridSvg");
        svg.innerHTML = "";

        const cellSize = 100;
        for (let r = 0; r < 4; r++) {
            for (let c = 0; c < 4; c++) {
                const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
                g.id = `cell-${r}-${c}`;
                g.setAttribute(
                    "transform",
                    `translate(${c * cellSize},${r * cellSize})`
                );

                const rect = document.createElementNS(
                    "http://www.w3.org/2000/svg",
                    "rect"
                );
                rect.setAttribute("width", cellSize);
                rect.setAttribute("height", cellSize);
                rect.setAttribute("fill", "#fff");

                const txt = document.createElementNS(
                    "http://www.w3.org/2000/svg",
                    "text"
                );
                txt.setAttribute("x", cellSize / 2);
                txt.setAttribute("y", cellSize / 2);
                txt.textContent = `${grid[r][c] ?? ''}`;

                g.appendChild(rect);
                g.appendChild(txt);
                svg.appendChild(g);
            }
        }
    }

    addEventListener("keyup", (event) => {
        evaluate(event.key);
    });

    function getGrid() {
        let grid = [];
        for (let row = 0; row < 4; row++) {
            grid.push([
                parseInt(document.querySelector(`#cell-${row}-0 text`).textContent) || null,
                parseInt(document.querySelector(`#cell-${row}-1 text`).textContent) || null,
                parseInt(document.querySelector(`#cell-${row}-2 text`).textContent) || null,
                parseInt(document.querySelector(`#cell-${row}-3 text`).textContent) || null,
            ]);
        }
        return grid;
    }

    function getMergeDirection(key) {
        let mergeDirection = "UP";
        switch (key) {
            case "ArrowUp":
                mergeDirection = "UP";
                break;
            case "ArrowDown":
                mergeDirection = "DOWN";
                break;
            case "ArrowLeft":
                mergeDirection = "LEFT";
                break;
            case "ArrowRight":
                mergeDirection = "RIGHT";
                break;
            default:
                return;
        }
        return mergeDirection;
    }

    function evaluate(key) {
        const mergeDirection = getMergeDirection(key);
        if (!mergeDirection) return;
        const serverUrl = document.getElementById('server-url').value

        fetch(`${serverUrl}/2048`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "grid": getGrid(),
                "mergeDirection": mergeDirection,
            }),
        })
            .then((res) => res.json())
            .then((data) => {
                renderGrid(data.nextGrid);
                document.getElementById("endGameText").textContent = getEndGameMessage(data.endGame);
            })
            .catch((error) => {
                window.alert('Error when connecting to logic server! Check log for details')
                console.error(error)
            });
    }

    const initialGrid = [
        [null, 2, null, null],
        [null, null, null, null],
        [null, null, 2, null],
        [null, null, null, null],
    ];
    renderGrid(initialGrid);
</script>
</body>
</html>'''
    return html_content, 200, {'Content-Type': 'text/html'}

@app.route('/2048/test', methods=['GET'])
def test_2048():
    """Test endpoint for 2048 game logic"""
    test_grid = [
        [2, 2, None, None],
        [4, 4, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]
    
    result = game_2048.process_move(test_grid, "LEFT")
    
    return jsonify({
        "test_input": {
            "grid": test_grid,
            "direction": "LEFT"
        },
        "result": result
    })
