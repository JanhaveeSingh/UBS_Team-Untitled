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
        self.grid_size = 4
        
    def is_valid_grid(self, grid: List[List]) -> bool:
        """Validate that the grid is 4x4 with valid values"""
        if not isinstance(grid, list) or len(grid) != 4:
            return False
        
        for row in grid:
            if not isinstance(row, list) or len(row) != 4:
                return False
            for cell in row:
                if cell is not None and (not isinstance(cell, int) or cell < 2 or (cell & (cell - 1)) != 0):
                    return False
        return True
    
    def add_random_tile(self, grid: List[List[Optional[int]]]) -> List[List[Optional[int]]]:
        """Add a random tile (2 or 4) to an empty cell"""
        # Find empty cells
        empty_cells = []
        for r in range(4):
            for c in range(4):
                if grid[r][c] is None:
                    empty_cells.append((r, c))
        
        if not empty_cells:
            return grid  # No empty cells
        
        # Choose random empty cell
        r, c = random.choice(empty_cells)
        
        # 90% chance for 2, 10% chance for 4
        grid[r][c] = 2 if random.random() < 0.9 else 4
        
        return grid
    
    def move_left(self, grid: List[List[Optional[int]]]) -> Tuple[List[List[Optional[int]]], bool]:
        """Move and merge tiles to the left, return (new_grid, changed)"""
        new_grid = [[None for _ in range(4)] for _ in range(4)]
        changed = False
        
        for r in range(4):
            # Collect non-None values from this row
            values = [cell for cell in grid[r] if cell is not None]
            
            # Merge adjacent equal values
            merged = []
            i = 0
            while i < len(values):
                if i + 1 < len(values) and values[i] == values[i + 1]:
                    # Merge the two tiles
                    merged.append(values[i] * 2)
                    i += 2  # Skip the next tile as it's been merged
                else:
                    merged.append(values[i])
                    i += 1
            
            # Fill the row with merged values and None
            for c in range(4):
                if c < len(merged):
                    new_grid[r][c] = merged[c]
                    if new_grid[r][c] != grid[r][c]:
                        changed = True
                else:
                    new_grid[r][c] = None
                    if grid[r][c] is not None:
                        changed = True
        
        return new_grid, changed
    
    def move_right(self, grid: List[List[Optional[int]]]) -> Tuple[List[List[Optional[int]]], bool]:
        """Move and merge tiles to the right"""
        # Reverse each row, move left, then reverse back
        reversed_grid = [row[::-1] for row in grid]
        moved_grid, changed = self.move_left(reversed_grid)
        result_grid = [row[::-1] for row in moved_grid]
        return result_grid, changed
    
    def move_up(self, grid: List[List[Optional[int]]]) -> Tuple[List[List[Optional[int]]], bool]:
        """Move and merge tiles upward"""
        # Transpose, move left, then transpose back
        transposed = [[grid[r][c] for r in range(4)] for c in range(4)]
        moved_transposed, changed = self.move_left(transposed)
        result_grid = [[moved_transposed[c][r] for c in range(4)] for r in range(4)]
        return result_grid, changed
    
    def move_down(self, grid: List[List[Optional[int]]]) -> Tuple[List[List[Optional[int]]], bool]:
        """Move and merge tiles downward"""
        # Transpose, move right, then transpose back
        transposed = [[grid[r][c] for r in range(4)] for c in range(4)]
        moved_transposed, changed = self.move_right(transposed)
        result_grid = [[moved_transposed[c][r] for c in range(4)] for r in range(4)]
        return result_grid, changed
    
    def make_move(self, grid: List[List[Optional[int]]], direction: str) -> Tuple[List[List[Optional[int]]], bool]:
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
    
    def check_win(self, grid: List[List[Optional[int]]]) -> bool:
        """Check if the player has won (reached 2048)"""
        for row in grid:
            for cell in row:
                if cell and cell >= 2048:
                    return True
        return False
    
    def can_move(self, grid: List[List[Optional[int]]]) -> bool:
        """Check if any moves are possible"""
        # Check for empty cells
        for row in grid:
            if None in row:
                return True
        
        # Check for possible merges horizontally
        for r in range(4):
            for c in range(3):
                if grid[r][c] == grid[r][c + 1]:
                    return True
        
        # Check for possible merges vertically
        for r in range(3):
            for c in range(4):
                if grid[r][c] == grid[r + 1][c]:
                    return True
        
        return False
    
    def process_move(self, grid: List[List[Optional[int]]], direction: str) -> Dict[str, Any]:
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
