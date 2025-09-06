"""
Micromouse Controller - Spec-compliant, momentum-aware planner
Drop-in replacement for your previous controller. Produces only legal instruction
sequences per the provided micromouse spec and logs inputs/errors for debugging.
"""

import logging
import traceback
from typing import Dict, List, Tuple, Optional, Any
from flask import request, jsonify

from routes import app

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MicromouseController:
    """Micromouse game state manager and controller (full spec compliance)"""

    def __init__(self):
        self.games: Dict[str, Dict[str, Any]] = {}

        # valid tokens set (core ones used by planner)
        self.valid_tokens = {
            # Longitudinal
            'F0', 'F1', 'F2', 'V0', 'V1', 'V2', 'BB',
            # In-place
            'L', 'R',
            # Moving rotations and corner forms may be produced selectively
            # But we'll generate only a conservative subset: F?L/F?R, F?LT/F?RT/F?LW/F?RW
            # to match simulator expectations
            'F0L', 'F0R', 'F1L', 'F1R', 'F2L', 'F2R',
            'F0LT', 'F0RT', 'F0LW', 'F0RW',
            'F1LT', 'F1RT', 'F1LW', 'F1RW',
            'F2LT', 'F2RT', 'F2LW', 'F2RW',
            # Reverse moving rotations - included for completeness but planner avoids illegal reversals
            'V0L', 'V0R', 'V1L', 'V1R', 'V2L', 'V2R'
        }

        # Base times (ms)
        self.base_times = {
            'in_place_turn': 200,
            'default_action': 200,
            'half_step_cardinal': 500,
            'half_step_intercardinal': 600,
            'corner_tight': 700,
            'corner_wide': 1400
        }

        # momentum reduction table
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

        # constants
        self.GRID_MIN = 0
        self.GRID_MAX = 15
        self.GOAL = (7, 7)  # representative (goal is 2x2: 7..8,7..8)
        self.TIME_BUDGET = 300_000
        self.THINKING_TIME_MS = 50

    # -------------------------------
    # Game lifecycle
    # -------------------------------
    def start_new_game(self, game_uuid: str, sensor_data: List[int],
                       total_time_ms: int = 0, goal_reached: bool = False,
                       best_time_ms: Optional[int] = None, run_time_ms: int = 0,
                       run: int = 0, momentum: int = 0, orientation: int = 0,
                       position: Optional[Tuple[int, int]] = None):
        if position is None:
            position = (0, 0)
        self.games[game_uuid] = {
            'sensor_data': (list(sensor_data)[:5] + [0]*5)[:5] if sensor_data else [0, 0, 0, 0, 0],
            'total_time_ms': total_time_ms,
            'goal_reached': goal_reached,
            'best_time_ms': best_time_ms,
            'run_time_ms': run_time_ms,
            'run': run,
            'momentum': momentum,
            'position': position,
            'orientation': orientation,  # 0 = North, then 45 increments
            'maze_map': {},  # (x,y) -> 'wall'|'passage' ; unknown means unexplored
            'visited_cells': set(),
            'path_to_goal': [],
            'current_run_started': False,
            'time_budget': self.TIME_BUDGET,
            'thinking_time': self.THINKING_TIME_MS
        }
        logger.info("Started new micromouse game %s (pos=%s orient=%s m=%s)", game_uuid, position, orientation, momentum)

    # -------------------------------
    # Public API - next instructions
    # -------------------------------
    def get_next_instructions(self, game_uuid: str) -> Tuple[List[str], bool]:
        if game_uuid not in self.games:
            return [], True
        game = self.games[game_uuid]

        # End conditions
        if game['total_time_ms'] >= game['time_budget'] or game['goal_reached'] or game['run'] >= 10:
            return [], True

        # Start run if needed
        if not game['current_run_started']:
            game['current_run_started'] = True
            game['run'] += 1
            game['run_time_ms'] = 0
            game['goal_reached'] = False
            game['position'] = (0, 0)
            game['orientation'] = 0
            game['momentum'] = 0
            logger.info("Starting run %d for game %s", game['run'], game_uuid)

        try:
            instrs = self._generate_movement_strategy(game_uuid)
            return instrs, False
        except Exception as e:
            # Log full payload and stack for debugging
            logger.error("Exception while generating movement instructions for %s: %s", game_uuid, str(e))
            logger.error(traceback.format_exc())
            # fail-safe: return brake to stop robot and avoid crash
            return ['BB'], False

    # -------------------------------
    # Planner
    # -------------------------------
    def _generate_movement_strategy(self, game_uuid: str) -> List[str]:
        game = self.games[game_uuid]
        pos = game['position']
        orient = game['orientation']
        momentum = game['momentum']
        sensors = (game['sensor_data'][:5] + [0]*5)[:5]

        # update map from sensors
        self._update_maze_map(game, pos, orient, sensors)

        # First check if we're completely blocked by walls
        # Check if front is blocked and we have momentum (would crash)
        if sensors[2] == 1 and momentum > 0:
            logger.warning("Front wall detected with forward momentum, braking to avoid crash")
            return ['BB']
        
        # Check if all main directions are blocked
        if sensors[0] == 1 and sensors[2] == 1 and sensors[4] == 1:
            # All three main directions blocked - just brake
            logger.warning("All main directions blocked, braking to avoid crash")
            return ['BB']

        # Check if we're in goal area but still moving - need to brake
        if self._is_in_goal_area(pos) and momentum > 0:
            logger.info("In goal area with momentum %s, braking to complete goal", momentum)
            return ['BB']
        
        # Try to find path to goal
        path = self._find_path_to_goal(game)
        if not path:
            # fallback exploration
            return self._exploration_strategy(game)

        # Convert path to token sequence while simulating momentum/orientation
        instrs = self._path_to_legal_instructions(game, path)
        # final safety check against immediate front wall in the same sensor frame
        final_guarded = self._apply_realtime_safety(game, instrs, sensors)
        
        # Additional safety: if we still have moving rotations after safety checks, replace with safe alternatives
        safe_instructions = []
        for instr in final_guarded[:5]:
            if instr in ('F0R', 'F1R', 'F2R', 'F0L', 'F1L', 'F2L'):
                # Replace moving rotation with brake + in-place turn + forward
                if instr.endswith('R'):
                    safe_instructions.extend(['BB', 'R', 'F2'])
                else:  # ends with 'L'
                    safe_instructions.extend(['BB', 'L', 'F2'])
                # Don't break - continue processing remaining instructions
            else:
                safe_instructions.append(instr)
        
        return safe_instructions[:5]

    # Build legal tokens from path respecting momentum/rotation rules
    def _path_to_legal_instructions(self, game: Dict[str, Any], path: List[Tuple[int, int]]) -> List[str]:
        if not path:
            return []
        instrs: List[str] = []
        # Use a local simulation of momentum & orientation for planning
        cur_pos = tuple(game['position'])
        cur_orient = int(game['orientation'])  # degrees: 0,45,90,...
        cur_mom = int(game['momentum'])
        
        # Get current sensor data for safety checks
        sensors = (game['sensor_data'][:5] + [0]*5)[:5]

        for next_cell in path:
            # validate cells
            if not isinstance(next_cell, tuple) or len(next_cell) != 2:
                logger.debug("Skipping invalid path cell: %s", next_cell)
                continue

            dx = next_cell[0] - cur_pos[0]
            dy = next_cell[1] - cur_pos[1]

            # Determine cardinal movement target and required orientation
            if dx == 1 and dy == 0:
                target_orient = 90
            elif dx == -1 and dy == 0:
                target_orient = 270
            elif dx == 0 and dy == 1:
                target_orient = 180
            elif dx == 0 and dy == -1:
                target_orient = 0
            else:
                # shouldn't happen for 4-connected path
                logger.debug("Non-cardinal neighbor in path: %s -> %s", cur_pos, next_cell)
                cur_pos = next_cell
                continue

            # Rotation needed (difference modulo 360)
            rot = (target_orient - cur_orient) % 360
            # Convert to sequence of 45° steps: we only use L/R as 45° each
            # If rot==90 -> one R, rot==270 -> one L, rot==180 -> R,R
            # But in-place rotation requires momentum == 0. We'll decide whether to brake or use moving-rotation.
            # Check whether a moving-rotation (translation+end-rotation) is possible instead.

            # Determine planned translation instruction if we were to do it without explicit brake
            # Choose acceleration token based on current momentum and desired forward direction
            # For simplicity, choose F2 to accelerate/maintain forward. But ensure we don't attempt F* when momentum sign conflicts.
            desired_dir_sign = 1  # We intend to move forward in path
            if cur_mom < 0:
                # moving forward while currently reverse momentum -> must brake to 0 first
                # Insert brakes until momentum is 0
                needed_brakes = self._brakes_needed_to_zero(cur_mom)
                instrs.extend(['BB'] * needed_brakes)
                cur_mom = self._simulate_brake_momentum(cur_mom, needed_brakes)
                # After braking, do in-place rotation if needed
            # Now attempt to see if moving-rotation can be used (allowed if m_eff <= 1)
            # We'll prefer moving-rotation only for single 45° rotations (rot == 90 or 270)
            use_moving_rotation = False
            moving_token = None

            # simulate m_out if we issue a forward accel/hold
            # choose forward action token to use: if cur_mom >=4 then F1 else F2 to accelerate
            if cur_mom <= 0:
                planned_token = 'F2'  # from rest or reverse -> accelerate forward (but reverse case handled above)
                planned_out_m = 1  # F2 always gives +1 momentum
            else:
                # have forward momentum
                planned_token = 'F2' if cur_mom < 4 else 'F1'
                planned_out_m = min(4, cur_mom + (1 if planned_token == 'F2' else 0))

            m_eff = (abs(cur_mom) + abs(planned_out_m)) / 2.0

            # handle cases where rot requires a moving rotation:
            # Be more conservative - only use moving rotation if we're sure it's safe
            if rot in (90, 270):
                # Check if there are walls that would block the moving rotation
                wall_blocking = False
                if rot == 90 and sensors[4] == 1:  # Right turn but right sensor sees wall
                    wall_blocking = True
                elif rot == 270 and sensors[0] == 1:  # Left turn but left sensor sees wall
                    wall_blocking = True
                
                # moving-rotation possible only if m_eff <= 1 AND we have very low momentum AND no walls blocking
                if m_eff <= 1.0 and cur_mom <= 1 and not wall_blocking:
                    # produce e.g. F1R or F2L depending on planned_token and rotation direction
                    suffix = 'R' if rot == 90 else 'L'
                    moving_token = planned_token + suffix
                    # additionally must ensure moving rotation direction agrees with momentum sign: forward tokens require non-negative momentum or 0
                    # cur_mom may be 0 or positive here
                    if cur_mom >= 0:
                        use_moving_rotation = True
                else:
                    use_moving_rotation = False

            # If rot == 180 we cannot do moving-rotation (it includes 2x45).
            # If use_moving_rotation -> append moving_token and update orientation and momentum
            if use_moving_rotation and moving_token in self.valid_tokens:
                instrs.append(moving_token)
                # update orientation and momentum simulation
                if rot == 90:
                    cur_orient = (cur_orient + 90) % 360
                else:
                    cur_orient = (cur_orient - 90) % 360
                # momentum update: planned_out_m
                cur_mom = planned_out_m
                # update position to next cell
                cur_pos = next_cell
                continue

            # Otherwise we must rotate in-place (L/R) which requires momentum 0
            if cur_mom != 0:
                # Insert brakes until momentum reaches 0
                brakes = self._brakes_needed_to_zero(cur_mom)
                instrs.extend(['BB'] * brakes)
                cur_mom = self._simulate_brake_momentum(cur_mom, brakes)

            # Now do rotation steps (45-degree L/R tokens)
            if rot == 90:
                instrs.append('R')
            elif rot == 270:
                instrs.append('L')
            elif rot == 180:
                instrs.extend(['R', 'R'])

            # Now do forward translation step (choose F2 or F1 according to cur_mom)
            if cur_mom <= 0:
                # from 0 or reverse (reverse handled earlier) -> accelerate forward
                instrs.append('F2')
                cur_mom = 1  # F2 always gives +1 momentum
            else:
                # moving forward already - keep accelerating or hold
                if cur_mom < 4:
                    instrs.append('F2')
                    cur_mom = min(4, cur_mom + 1)
                else:
                    instrs.append('F1')
                    # cur_mom remains 4

            # update orientation and position
            cur_orient = target_orient
            cur_pos = next_cell

        return instrs

    # Return number of BB needed to reach zero momentum (each BB reduces magnitude by 2 toward 0)
    def _brakes_needed_to_zero(self, momentum: int) -> int:
        m = abs(momentum)
        if m == 0:
            return 0
        # each BB reduces magnitude by 2 toward 0 (but still moves half-step in that direction according to spec)
        # compute ceiling(m / 2)
        import math
        return math.ceil(m / 2.0)

    # Simulate momentum after applying N brakes
    def _simulate_brake_momentum(self, momentum: int, brake_count: int) -> int:
        m = momentum
        for _ in range(brake_count):
            if m > 0:
                m = max(0, m - 2)
            elif m < 0:
                m = min(0, m + 2)
        return m

    # Apply real-time safety using current sensor frame:
    # - prevent immediate forward into front wall
    # - prevent turn followed by forward into known side wall (left/right)
    def _apply_realtime_safety(self, game: Dict[str, Any], instrs: List[str], sensors: List[int]) -> List[str]:
        if not instrs:
            return []
        sensors = (sensors[:5] + [0]*5)[:5]
        out: List[str] = []
        
        # Track current orientation for safety checks
        current_orient = game.get('orientation', 0)
        current_momentum = game.get('momentum', 0)
        
        for i, tok in enumerate(instrs):
            # prevent any in-place rotation when momentum !=0 (double-check)
            if tok in ('L', 'R') and current_momentum != 0:
                logger.warning("Real-time safety blocked in-place rotation due to nonzero momentum (payload momentum=%s)", current_momentum)
                return ['BB']
            
            # Check for moving rotations that would hit walls
            if tok in ('F0R', 'F1R', 'F2R', 'F0L', 'F1L', 'F2L'):
                # Extract the rotation direction
                if tok.endswith('R'):
                    # Right turn - check if there's a wall to the right after the turn
                    if sensors[1]:  # Right sensor detects wall
                        logger.warning("Real-time safety: right wall detected; blocking moving rotation %s", tok)
                        return ['BB']
                elif tok.endswith('L'):
                    # Left turn - check if there's a wall to the left after the turn
                    if sensors[0]:  # Left sensor detects wall
                        logger.warning("Real-time safety: left wall detected; blocking moving rotation %s", tok)
                        return ['BB']
            
            # If about to go forward (first forward token), but front sensor sees a wall, block
            if i == 0 and tok.startswith('F') and not tok.endswith(('L', 'R')):
                if sensors[2]:  # Front sensor detects wall
                    logger.warning("Real-time safety: front wall detected; blocking forward token %s", tok)
                    return ['BB']
            
            # If sequence starts with rotation then forward, and side sensor reports wall, block
            if i == 1 and tok.startswith('F') and len(out) >= 1 and out[0] in ('L', 'R'):
                turn = out[0]
                if turn == 'L' and sensors[0]:
                    logger.warning("Real-time safety: left wall would block forward after left turn -> blocking")
                    return ['BB']
                if turn == 'R' and sensors[4]:
                    logger.warning("Real-time safety: right wall would block forward after right turn -> blocking")
                    return ['BB']
            
            # Additional safety: if we have high momentum and front wall, brake immediately
            if tok.startswith('F') and not tok.endswith(('L', 'R')) and current_momentum > 2 and sensors[2]:
                logger.warning("Real-time safety: high momentum (%s) with front wall, braking", current_momentum)
                return ['BB']
            
            out.append(tok)
            if len(out) >= 5:
                break
        return out

    # -------------------------------
    # Exploration (fallback)
    # -------------------------------
    def _exploration_strategy(self, game: Dict[str, Any]) -> List[str]:
        # conservative exploration that never crashes: prefer braking then turning only at zero momentum
        pos = game['position']
        mom = game['momentum']
        sensors = (game['sensor_data'][:5] + [0]*5)[:5]

        # if front is free and momentum >=0 => move forward (accelerate or hold)
        if sensors[2] == 0 and mom >= 0:
            if mom < 4:
                return ['F2']
            else:
                return ['F1']

        # If front blocked, try to turn to an open side, but ensure momentum = 0
        # Check right then left then U-turn (right preferred)
        if mom != 0:
            # brake first
            return ['BB']
        
        # mom == 0, now check for safe turns
        # Check right side first
        if sensors[4] == 0:  # Right side is clear
            return ['R', 'F2']
        # Check left side
        if sensors[0] == 0:  # Left side is clear
            return ['L', 'F2']
        
        # All sides blocked - just brake and wait
        logger.warning("Exploration: All sides blocked, braking to avoid crash")
        return ['BB']

    # -------------------------------
    # Maze mapping & helpers
    # -------------------------------
    def _update_maze_map(self, game: Dict[str, Any], position: Tuple[int, int], orientation: int, sensor_data: List[int]):
        if not isinstance(position, tuple) or len(position) != 2:
            logger.error("Invalid position for map update: %s", position)
            return
        x, y = position
        sensor_angles = [-90, -45, 0, 45, 90]
        for i in range(min(5, len(sensor_data))):
            ang = sensor_angles[i]
            p = self._get_wall_position(x, y, orientation, ang)
            if p is None:
                continue
            if sensor_data[i] > 0:
                game['maze_map'][p] = 'wall'
            else:
                # only mark passage if we don't already know a wall
                if game['maze_map'].get(p) != 'wall':
                    game['maze_map'][p] = 'passage'

    def _get_wall_position(self, x: int, y: int, orientation: int, sensor_angle: int) -> Optional[Tuple[int, int]]:
        absolute_angle = (orientation + sensor_angle) % 360
        # Map to delta (dx,dy) using grid coordinates where y increases southward per your code
        if absolute_angle == 0:
            nx, ny = x, y - 1
        elif absolute_angle == 45:
            nx, ny = x + 1, y - 1
        elif absolute_angle == 90:
            nx, ny = x + 1, y
        elif absolute_angle == 135:
            nx, ny = x + 1, y + 1
        elif absolute_angle == 180:
            nx, ny = x, y + 1
        elif absolute_angle == 225:
            nx, ny = x - 1, y + 1
        elif absolute_angle == 270:
            nx, ny = x - 1, y
        elif absolute_angle == 315:
            nx, ny = x - 1, y - 1
        else:
            return None
        if 0 <= nx <= self.GRID_MAX and 0 <= ny <= self.GRID_MAX:
            return (nx, ny)
        return None

    # -------------------------------
    # Pathfinding (A*)
    # -------------------------------
    def _find_path_to_goal(self, game: Dict[str, Any]) -> List[Tuple[int, int]]:
        start = game['position']
        goal = self.GOAL
        if not isinstance(start, tuple) or len(start) != 2:
            logger.error("Invalid start position for pathfinding: %s", start)
            return []
        if start == goal:
            return []
        open_set: List[Tuple[int, Tuple[int, int]]] = [(0, start)]
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, goal)}

        while open_set:
            current = min(open_set, key=lambda x: x[0])[1]
            open_set = [item for item in open_set if item[1] != current]
            if current == goal:
                # reconstruct
                path: List[Tuple[int, int]] = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            neighbors = self._get_neighbors(current, game['maze_map'])
            for n in neighbors:
                tentative = g_score[current] + 1
                if n not in g_score or tentative < g_score[n]:
                    came_from[n] = current
                    g_score[n] = tentative
                    f_score[n] = tentative + self._heuristic(n, goal)
                    if not any(item[1] == n for item in open_set):
                        open_set.append((f_score[n], n))
        return []

    def _get_neighbors(self, position: Tuple[int, int], maze_map: Dict) -> List[Tuple[int, int]]:
        if not isinstance(position, tuple) or len(position) != 2:
            logger.error("Invalid position in neighbors: %s", position)
            return []
        x, y = position
        neighbors = []
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # N, E, S, W given your orientation mapping
            nx, ny = x + dx, y + dy
            if 0 <= nx <= self.GRID_MAX and 0 <= ny <= self.GRID_MAX:
                # only skip if known wall
                if maze_map.get((nx, ny)) == 'wall':
                    continue
                neighbors.append((nx, ny))
        return neighbors

    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # -------------------------------
    # Movement time & scoring (kept for completeness)
    # -------------------------------
    def calculate_movement_time(self, instruction: str, momentum_in: int, momentum_out: int) -> int:
        if instruction in ('L', 'R'):
            return self.base_times['in_place_turn']
        if instruction == 'BB' and momentum_in == 0:
            return self.base_times['default_action']
        m_eff = (abs(momentum_in) + abs(momentum_out)) / 2.0
        if instruction in ('F0', 'F1', 'F2', 'V0', 'V1', 'V2', 'BB'):
            base = self.base_times['half_step_cardinal'] if self._is_cardinal(instruction) else self.base_times['half_step_intercardinal']
        elif 'T' in instruction:
            base = self.base_times['corner_tight']
        elif 'W' in instruction:
            base = self.base_times['corner_wide']
        else:
            base = self.base_times['default_action']
        reduction = self._get_momentum_reduction(m_eff)
        return int(round(base * (1 - reduction)))

    def _is_cardinal(self, instruction: str) -> bool:
        return instruction in ('F0', 'F1', 'F2', 'V0', 'V1', 'V2', 'BB')

    def _get_momentum_reduction(self, m_eff: float) -> float:
        m_eff = max(0.0, min(4.0, m_eff))
        keys = sorted(self.momentum_reduction.keys())
        if m_eff <= keys[0]:
            return self.momentum_reduction[keys[0]]
        if m_eff >= keys[-1]:
            return self.momentum_reduction[keys[-1]]
        for i in range(len(keys) - 1):
            if keys[i] <= m_eff <= keys[i + 1]:
                x1, y1 = keys[i], self.momentum_reduction[keys[i]]
                x2, y2 = keys[i + 1], self.momentum_reduction[keys[i + 1]]
                return y1 + (y2 - y1) * (m_eff - x1) / (x2 - x1)
        return 0.0

    def calculate_score(self, total_time_ms: int, best_time_ms: Optional[int]) -> float:
        if best_time_ms is None:
            return float('inf')
        return (1/30.0) * total_time_ms + best_time_ms

    # -------------------------------
    # State updates
    # -------------------------------
    def update_game_state(self, game_uuid: str, new_state: Dict[str, Any]):
        if game_uuid not in self.games:
            logger.warning("Update received for unknown game %s", game_uuid)
            return
        game = self.games[game_uuid]
        # update safe fields
        if 'sensor_data' in new_state:
            sd = new_state['sensor_data']
            if sd is None:
                game['sensor_data'] = [0, 0, 0, 0, 0]
            else:
                game['sensor_data'] = (list(sd)[:5] + [0]*5)[:5]
        for key in ('total_time_ms', 'goal_reached', 'best_time_ms', 'run_time_ms', 'run', 'momentum', 'orientation'):
            if key in new_state:
                game[key] = new_state[key]
        if 'position' in new_state and isinstance(new_state['position'], (list, tuple)) and len(new_state['position']) == 2:
            # ensure ints and bounds
            px, py = int(new_state['position'][0]), int(new_state['position'][1])
            px = max(self.GRID_MIN, min(self.GRID_MAX, px))
            py = max(self.GRID_MIN, min(self.GRID_MAX, py))
            game['position'] = (px, py)

        # Update position from momentum (coarse simulation)
        self._update_position_from_momentum(game)

        # Check goal reached
        if self._is_in_goal_area(game['position']):
            if game.get('momentum', 0) == 0:
                game['goal_reached'] = True
                if game['best_time_ms'] is None or game['run_time_ms'] < game['best_time_ms']:
                    game['best_time_ms'] = game['run_time_ms']
                logger.info("Game %s reached goal! run_time_ms=%s", game_uuid, game['run_time_ms'])
            else:
                # In goal area but still moving - need to brake
                logger.info("Game %s in goal area but still moving (momentum=%s), need to brake", game_uuid, game.get('momentum', 0))

        # If back at origin with momentum 0 -> new run possible
        if game['position'] == (0, 0) and game.get('momentum', 0) == 0:
            game['current_run_started'] = False

    def _update_position_from_momentum(self, game: Dict[str, Any]):
        m = game.get('momentum', 0)
        if m == 0:
            return
        x, y = game['position']
        orient = game.get('orientation', 0)
        dx = dy = 0
        if orient == 0:
            dy = -1
        elif orient == 45:
            dx, dy = 1, -1
        elif orient == 90:
            dx = 1
        elif orient == 135:
            dx, dy = 1, 1
        elif orient == 180:
            dy = 1
        elif orient == 225:
            dx, dy = -1, 1
        elif orient == 270:
            dx = -1
        elif orient == 315:
            dx, dy = -1, -1
        
        # Move in the direction of momentum (positive = forward, negative = backward)
        steps = abs(m)
        if m < 0:  # Reverse momentum - move opposite direction
            dx, dy = -dx, -dy
        
        nx, ny = x + dx * steps, y + dy * steps
        nx = max(self.GRID_MIN, min(self.GRID_MAX, nx))
        ny = max(self.GRID_MIN, min(self.GRID_MAX, ny))
        game['position'] = (nx, ny)

    def _is_in_goal_area(self, position: Tuple[int, int]) -> bool:
        if not isinstance(position, tuple) or len(position) != 2:
            return False
        x, y = position
        return 7 <= x <= 8 and 7 <= y <= 8


# -------------------------------
# Global manager & Flask endpoints
# -------------------------------
game_manager = MicromouseController()


@app.route('/micro-mouse', methods=['POST'])
def micromouse():
    """
    Main endpoint for micromouse controller - guarded and logs payloads on error.
    """
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({'error': 'Empty request body'}), 400
        game_uuid = payload.get('game_uuid')
        if not game_uuid:
            return jsonify({'error': 'Missing game_uuid'}), 400

        # Create or update
        if game_uuid not in game_manager.games:
            logger.info("Initializing new game %s with payload: %s", game_uuid, payload)
            try:
                game_manager.start_new_game(
                    game_uuid=game_uuid,
                    sensor_data=payload.get('sensor_data', [0, 0, 0, 0, 0]),
                    total_time_ms=payload.get('total_time_ms', 0),
                    goal_reached=payload.get('goal_reached', False),
                    best_time_ms=payload.get('best_time_ms'),
                    run_time_ms=payload.get('run_time_ms', 0),
                    run=payload.get('run', 0),
                    momentum=payload.get('momentum', 0),
                    orientation=payload.get('orientation', 0),
                    position=tuple(payload.get('position', (0, 0)))
                )
            except Exception as e:
                logger.error("Error starting game %s: %s", game_uuid, str(e))
                logger.error(traceback.format_exc())
                return jsonify({'error': 'Internal server error while starting game'}), 500
        else:
            logger.info("Updating existing game %s with payload: %s", game_uuid, payload)
            try:
                game_manager.update_game_state(game_uuid, payload)
            except Exception as e:
                # log full payload and traceback for debugging on Render
                logger.error("Error updating game state for %s: %s", game_uuid, str(e))
                logger.error("Payload was: %s", payload)
                logger.error(traceback.format_exc())
                # continue; we will still try to produce safe instructions

        try:
            instructions, end_flag = game_manager.get_next_instructions(game_uuid)
        except Exception as e:
            logger.error("Exception producing instructions for %s: %s", game_uuid, str(e))
            logger.error("Payload was: %s", payload)
            logger.error(traceback.format_exc())
            # safe fallback
            instructions, end_flag = ['BB'], True

        # Charge thinking time externally per spec (server/simulator handles time; here we simply respond)
        response = {'instructions': instructions, 'end': end_flag}
        logger.info("Micromouse %s -> instructions=%s end=%s", game_uuid, instructions, end_flag)
        return jsonify(response)
    except Exception as e:
        # log payload if available
        try:
            payload = request.get_json(force=False)
            logger.error("Unhandled exception in /micro-mouse. Payload: %s", payload)
        except Exception:
            logger.error("Unhandled exception in /micro-mouse, payload unavailable.")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/micro-mouse/stats/<game_uuid>', methods=['GET'])
def get_micromouse_stats(game_uuid):
    try:
        stats = game_manager.games.get(game_uuid)
        if not stats:
            return jsonify({'error': 'Game not found'}), 404
        out = {
            'position': stats['position'],
            'orientation': stats['orientation'],
            'momentum': stats['momentum'],
            'run': stats['run'],
            'run_time_ms': stats['run_time_ms'],
            'best_time_ms': stats['best_time_ms'],
            'goal_reached': stats['goal_reached'],
            'total_time_ms': stats['total_time_ms'],
            'time_remaining': stats['time_budget'] - stats['total_time_ms']
        }
        return jsonify(out)
    except Exception:
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/micro-mouse/debug/<game_uuid>', methods=['GET'])
def get_micromouse_debug(game_uuid):
    try:
        if game_uuid not in game_manager.games:
            return jsonify({'error': 'Game not found'}), 404
        g = game_manager.games[game_uuid]
        debug_info = {
            'position': g['position'],
            'position_type': str(type(g['position'])),
            'orientation': g['orientation'],
            'momentum': g['momentum'],
            'sensor_data': g['sensor_data'],
            'maze_map': dict(g['maze_map']),
            'visited_cells': list(g['visited_cells']),
            'run': g['run'],
            'goal_reached': g['goal_reached']
        }
        return jsonify(debug_info)
    except Exception:
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500
