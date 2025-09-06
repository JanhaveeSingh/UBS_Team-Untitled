"""
Micromouse Controller - AI-Enhanced implementation
Implements the micromouse movement specification with OpenAI-powered decision making.
"""

import logging
import traceback
import math
import os
import json
from collections import deque
from typing import Dict, List, Tuple, Optional, Any
from flask import request, jsonify

# Console-like logging for JavaScript-style debugging
class Console:
    @staticmethod
    def info(*args):
        message = ' '.join(str(arg) for arg in args)
        print(f"[CONSOLE.INFO] {message}")
        
    @staticmethod
    def log(*args):
        message = ' '.join(str(arg) for arg in args)
        print(f"[CONSOLE.LOG] {message}")

console = Console()

try:
    import openai
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    OPENAI_AVAILABLE = bool(openai.api_key)
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

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
            
            # Internal state for pathfinding and exploration
            'last_sensors': [0, 0, 0, 0, 0],
            'recent_moves': deque(maxlen=10),  # For loop detection
            'stuck_counter': 0,
            'exploration_phase': True,  # Start in exploration mode
            'wall_follow_side': 'right',  # Which wall to follow
            'ai_enabled': OPENAI_AVAILABLE  # Track if AI is available
        }
        logger.info(f"Started new game {game_uuid} (AI: {'enabled' if OPENAI_AVAILABLE else 'disabled'})")

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
        goal_reached = game.get('goal_reached', False)
        
        console.info("🧠 STRATEGY INPUT:")
        console.info(f"  Momentum: {momentum}")
        console.info(f"  Goal Reached: {goal_reached}")
        console.info(f"  Sensors: {sensors}")
        
        logger.info(f"Current state - Momentum: {momentum}, Goal reached: {goal_reached}, Sensors: {sensors}")
        
        # If goal is reached and we have momentum, brake to complete
        if goal_reached and momentum != 0:
            console.info("🎯 Decision: Goal reached with momentum, braking to complete")
            logger.info("Goal reached with momentum, braking to complete")
            return ['BB']
        
        # If goal is reached and stopped, we're done
        if goal_reached and momentum == 0:
            console.info("🏆 Decision: Goal reached and stopped!")
            logger.info("Goal reached and stopped!")
            return []
        
        # Safety first - if we have momentum and front wall, brake
        if momentum > 0 and len(sensors) > 2 and sensors[2] == 1:  # Front sensor detects wall
            console.info("🚨 Decision: Front wall detected with forward momentum, emergency braking")
            logger.info("Front wall detected with forward momentum, braking")
            return ['BB']
        
        # Detect if stuck in loop
        if self._is_stuck_in_loop(game):
            console.info("🔄 Decision: Loop detected, calling escape strategy")
            return self._escape_loop(game)
        
        # Use AI-enhanced strategy if available, otherwise fall back to wall following
        if OPENAI_AVAILABLE and game.get('total_time_ms', 0) < 250000:  # Use AI for first 250 seconds
            console.info("🤖 Decision: Using AI-enhanced strategy")
            return self._ai_enhanced_strategy(game)
        else:
            console.info("🧱 Decision: Using wall-following strategy")
            return self._wall_follow_strategy(game)

    def _wall_follow_strategy(self, game: Dict[str, Any]) -> List[str]:
        """Implement right-hand wall following strategy using only sensor data"""
        momentum = game['momentum']
        sensors = game['sensor_data'][:5] if len(game['sensor_data']) >= 5 else [0, 0, 0, 0, 0]
        
        # Sensors are: [left(-90°), left-front(-45°), front(0°), right-front(45°), right(90°)]
        left, left_front, front, right_front, right = sensors
        
        # Critical: Handle momentum constraints first
        if momentum > 0:
            # If there's a wall ahead, must brake immediately
            if front == 1:
                console.info("🚨 Wall Following: Emergency braking due to front wall")
                logger.info("Wall ahead with forward momentum, emergency braking")
                return ['BB']
            # If no immediate obstacle, can continue but be cautious
            console.info(f"🏃 Wall Following: Moving forward with momentum {momentum}")
            logger.info(f"Moving forward with momentum {momentum}")
            # Use F0 to decelerate if at high speed, F1 to maintain
            result = ['F0'] if momentum >= 3 else ['F1']
            console.info(f"✅ Wall Following Output: {result}")
            return result
        elif momentum < 0:
            # If moving backward, brake to stop
            console.info("🔄 Wall Following: Braking to stop backward movement")
            logger.info("Moving backward, braking to stop")
            return ['BB']
        
        # At rest (momentum == 0), apply right-hand rule safely
        # Priority 1: Turn right if right wall is clear and no immediate obstacles
        if right == 0 and front != 1:  # Right clear and front not blocked
            console.info("➡️ Wall Following: Right side clear, turning right")
            logger.info("Right side clear, turning right")
            return ['R']
        
        # Priority 2: Go forward if front is clear
        if front == 0:
            console.info("⬆️ Wall Following: Front clear, moving forward")
            logger.info("Front clear, moving forward")
            return ['F1']
        
        # Priority 3: Turn left if left is clear
        if left == 0:
            console.info("⬅️ Wall Following: Left side clear, turning left")
            logger.info("Left side clear, turning left")
            return ['L']
        
        # Priority 4: If stuck, just turn right (will eventually find opening)
        console.info("🔄 Wall Following: All sides blocked, turning right to explore")
        logger.info("All sides blocked, turning right to explore")
        result = ['R']
        console.info(f"✅ Wall Following Output: {result}")
        return result

    def _is_stuck_in_loop(self, game: Dict[str, Any]) -> bool:
        """Detect if mouse is stuck in a repetitive pattern based on sensor readings"""
        sensors = tuple(game['sensor_data'][:5])
        recent_moves = game['recent_moves']
        
        # Add current sensor state to recent moves
        recent_moves.append(sensors)
        
        # Check if we've seen the same sensor pattern too often recently
        if len(recent_moves) >= 6:
            recent_patterns = list(recent_moves)[-6:]
            pattern_count = {}
            for pattern in recent_patterns:
                pattern_count[pattern] = pattern_count.get(pattern, 0) + 1
            
            # If any pattern appears more than 3 times in recent moves, we're stuck
            for count in pattern_count.values():
                if count >= 4:
                    game['stuck_counter'] += 1
                    return game['stuck_counter'] >= 2
        
        return False

    def _escape_loop(self, game: Dict[str, Any]) -> List[str]:
        """Escape from detected loop by trying different approach"""
        logger.info("Loop detected, attempting escape")
        game['stuck_counter'] = 0  # Reset counter
        
        momentum = game['momentum']
        sensors = game['sensor_data'][:5]
        
        # If we have momentum, we must handle it first before any rotation
        if momentum != 0:
            # If front is blocked, brake
            if len(sensors) > 2 and sensors[2] == 1:  # Front wall
                logger.info("Escape: braking due to front wall")
                return ['BB']
            # Otherwise continue forward to clear momentum
            logger.info("Escape: continuing forward to clear momentum")
            return ['F0']  # Decelerate while moving forward
        
        # Only try AI or rotations when at rest (momentum == 0)
        if OPENAI_AVAILABLE:
            try:
                prompt = f"""The micromouse is stuck in a loop and is now at rest (momentum 0). Help it escape!

Current state:
- Sensors (left, left-front, front, right-front, right): {sensors} (1=wall, 0=clear)
- Momentum: {momentum} (at rest)
- Stuck counter was reset

The mouse has been repeating the same movements. Choose a safe move to break the pattern.
Only use moves valid at momentum 0: F0, F1, F2, V0, V1, V2, BB, L, R

Respond with only a JSON array of 1-2 movement tokens, e.g., ["L"] or ["F1"]"""

                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are helping a micromouse escape from a stuck loop. Only suggest moves valid for momentum 0."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=30,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content.strip()
                instructions = json.loads(ai_response)
                
                if isinstance(instructions, list) and all(isinstance(token, str) for token in instructions):
                    valid_instructions = [token for token in instructions if token in self.valid_tokens]
                    if valid_instructions:
                        logger.info(f"AI escape strategy: {valid_instructions}")
                        return valid_instructions
                        
            except Exception as e:
                logger.info(f"AI escape failed: {e}")
        
        # Fallback to traditional escape logic (only when momentum == 0)
        left, left_front, front, right_front, right = sensors
        
        # Try opposite of normal right-hand rule: prefer left
        if left == 0:  # Left clear
            logger.info("Escape: turning left")
            return ['L']
        
        # Try going straight if possible
        if front == 0:  # Front clear
            logger.info("Escape: moving forward")
            return ['F1']
        
        # Try right if available
        if right == 0:  # Right clear
            logger.info("Escape: turning right")
            return ['R']
        
        # Last resort: turn around (two right turns)
        logger.info("Escape: turning around")
        return ['R']  # Just one turn for now, will turn again next cycle

    def _ai_enhanced_strategy(self, game: Dict[str, Any]) -> List[str]:
        """Use OpenAI to make intelligent navigation decisions"""
        if not OPENAI_AVAILABLE:
            logger.info("OpenAI not available, falling back to wall following")
            return self._wall_follow_strategy(game)
        
        try:
            # Prepare context for AI
            sensors = game['sensor_data'][:5]
            momentum = game['momentum']
            goal_reached = game.get('goal_reached', False)
            run_time = game.get('run_time_ms', 0)
            total_time = game.get('total_time_ms', 0)
            run_number = game.get('run', 0)
            
            # Create a prompt for the AI
            prompt = f"""You are controlling a micromouse in a 16x16 maze. Your goal is to reach the 2x2 center goal as quickly as possible.

Current state:
- Sensors (left, left-front, front, right-front, right): {sensors} (1=wall, 0=clear)
- Momentum: {momentum} (range -4 to +4, currently {'stopped' if momentum == 0 else 'moving'})
- Goal reached: {goal_reached}
- Current run time: {run_time}ms
- Total time used: {total_time}ms / 300000ms budget
- Run number: {run_number}

CRITICAL MOVEMENT RULES:
- Rotations (L, R) ONLY allowed when momentum = 0
- With momentum ≠ 0, you can only use: F0, F1, F2, V0, V1, V2, BB
- Moving rotations (F0L, F1R, etc.) only if effective momentum ≤ 1
- If momentum > 0 and front sensor = 1 (wall), you MUST brake (BB)

Available tokens based on current momentum {momentum}:
{'- ALL tokens available (including L, R)' if momentum == 0 else '- Only longitudinal: F0, F1, F2, V0, V1, V2, BB (NO rotations L/R)'}

Safety first: If front wall detected with forward momentum, use BB to brake.

Choose 1-3 movement tokens that respect momentum rules. Consider:
1. SAFETY: Don't crash into walls
2. MOMENTUM RULES: No L/R unless momentum = 0
3. Exploration using right-hand rule when safe

Respond with only a JSON array of movement tokens, e.g., ["F1"] or ["BB"]"""

            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert micromouse maze navigation AI. Always respond with valid JSON arrays of movement tokens."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.3
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            console.info(f"🤖 AI Raw Response: {ai_response}")
            logger.info(f"AI response: {ai_response}")
            
            # Try to parse as JSON
            try:
                instructions = json.loads(ai_response)
                if isinstance(instructions, list) and all(isinstance(token, str) for token in instructions):
                    # Validate tokens are in our valid set
                    valid_instructions = [token for token in instructions if token in self.valid_tokens]
                    
                    # Additional validation: check momentum constraints
                    if momentum != 0:
                        # Filter out rotations when momentum is not zero
                        safe_instructions = []
                        for token in valid_instructions:
                            if token in ['L', 'R']:  # Pure rotations not allowed with momentum
                                console.info(f"🚫 Filtered out rotation {token} due to momentum {momentum}")
                                logger.info(f"Filtered out rotation {token} due to momentum {momentum}")
                                continue
                            safe_instructions.append(token)
                        valid_instructions = safe_instructions
                    
                    if valid_instructions:
                        console.info(f"✅ AI Strategy Output: {valid_instructions}")
                        logger.info(f"AI strategy selected: {valid_instructions}")
                        return valid_instructions
            except json.JSONDecodeError:
                logger.info("Failed to parse AI response as JSON")
            
        except Exception as e:
            logger.info(f"AI strategy failed: {e}")
        
        # Fallback to traditional strategy
        logger.info("Falling back to wall following strategy")
        return self._wall_follow_strategy(game)

    def update_game_state(self, game_uuid: str, new_state: Dict[str, Any]):
        """Update game state from API payload"""
        if game_uuid not in self.games:
            logger.info(f"Update for unknown game {game_uuid}")
            return
            
        game = self.games[game_uuid]
        
        # Update fields from API spec
        for field in ['sensor_data', 'total_time_ms', 'goal_reached', 
                     'best_time_ms', 'run_time_ms', 'run', 'momentum']:
            if field in new_state:
                game[field] = new_state[field]
        
        # Ensure sensor_data is always 5 elements
        if 'sensor_data' in new_state:
            sensors = new_state['sensor_data'] or [0, 0, 0, 0, 0]
            game['sensor_data'] = (list(sensors)[:5] + [0]*5)[:5]
        
        # Store previous sensor state for comparison
        if 'last_sensors' in game:
            game['last_sensors'] = game['sensor_data'][:]
        
        # Log important state changes
        if new_state.get('goal_reached', False):
            logger.info(f"Goal reached! Run: {game.get('run', 0)}, Time: {game.get('run_time_ms', 0)}ms")
        
        if new_state.get('run', 0) > game.get('run', 0):
            logger.info(f"New run started: {new_state['run']}")
            # Reset some internal state for new run
            game['stuck_counter'] = 0
            game['recent_moves'].clear()

# Global controller instance
controller = MicromouseController()

@app.route('/micro-mouse', methods=['POST'])
def micromouse():
    """Main micromouse endpoint per API specification"""
    try:
        payload = request.get_json(force=True)
        if not payload:
            console.info("❌ ERROR: Empty request body received")
            return jsonify({'error': 'Empty request body'}), 400
            
        game_uuid = payload.get('game_uuid')
        if not game_uuid:
            console.info("❌ ERROR: Missing game_uuid in request")
            return jsonify({'error': 'Missing game_uuid'}), 400

        # Log detailed input information
        console.info("🎮 MICROMOUSE INPUT:")
        console.info(f"  Game UUID: {game_uuid}")
        console.info(f"  Sensors: {payload.get('sensor_data', 'N/A')}")
        console.info(f"  Momentum: {payload.get('momentum', 'N/A')}")
        console.info(f"  Goal Reached: {payload.get('goal_reached', 'N/A')}")
        console.info(f"  Total Time: {payload.get('total_time_ms', 'N/A')}ms")
        console.info(f"  Run: {payload.get('run', 'N/A')}")
        console.info(f"  Full Payload: {payload}")

        # Initialize or update game
        if game_uuid not in controller.games:
            logger.info(f"Starting new game {game_uuid}")
            console.info(f"🆕 Starting new game {game_uuid}")
            # Remove game_uuid from payload to avoid duplicate argument
            init_payload = {k: v for k, v in payload.items() if k != 'game_uuid'}
            controller.start_new_game(game_uuid, **init_payload)
        else:
            logger.info(f"Updating game {game_uuid}")
            console.info(f"🔄 Updating existing game {game_uuid}")
            controller.update_game_state(game_uuid, payload)

        # Generate instructions
        instructions, end_flag = controller.get_next_instructions(game_uuid)
        
        response = {
            'instructions': instructions,
            'end': end_flag
        }
        
        # Log detailed output information
        console.info("🚀 MICROMOUSE OUTPUT:")
        console.info(f"  Game UUID: {game_uuid}")
        console.info(f"  Instructions: {instructions}")
        console.info(f"  End Flag: {end_flag}")
        console.info(f"  Full Response: {response}")
        
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
            'momentum': game['momentum'],
            'run': game['run'],
            'run_time_ms': game['run_time_ms'],
            'best_time_ms': game['best_time_ms'],
            'goal_reached': game['goal_reached'],
            'total_time_ms': game['total_time_ms'],
            'time_remaining': controller.TIME_BUDGET - game['total_time_ms'],
            'sensor_data': game['sensor_data']
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
            'momentum': game['momentum'],
            'sensor_data': game['sensor_data'],
            'run': game['run'],
            'goal_reached': game['goal_reached'],
            'stuck_counter': game.get('stuck_counter', 0),
            'wall_follow_side': game.get('wall_follow_side', 'right'),
            'recent_moves': list(game.get('recent_moves', [])),
            'exploration_phase': game.get('exploration_phase', True),
            'ai_enabled': game.get('ai_enabled', False),
            'openai_available': OPENAI_AVAILABLE
        }
        return jsonify(debug_info)
        
    except Exception as e:
        logger.info(f"Error getting debug info: {e}")
        return jsonify({'error': 'Internal server error'}), 500
