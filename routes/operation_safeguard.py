import os
import sys
import logging
from flask import request, jsonify
import requests
import json
from dotenv import load_dotenv

# Add parent directory to path to allow importing routes module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging

from flask import request

from routes import app




logger = logging.getLogger(__name__)

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_PROJECT = os.environ.get("OPENAI_PROJECT")

# OpenAI API configuration
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.1
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

# AI fallback configuration
ENABLE_AI_FALLBACK = True

# Cipher configuration constants
class config:
    DEFAULT_RAILFENCE_RAILS = 3
    DEFAULT_KEYWORD = "SHADOW"
    DEFAULT_CAESAR_SHIFT = 13
    MEANINGFUL_WORDS = ["MISSION", "TARGET", "AGENT", "OPERATION", "SECURE", "CONFIRM", "COMPLETE", "STATUS", "REPORT", "INTEL"]


def detect_ascii_patterns(coords):
    """Detect if coordinates form ASCII art patterns like letters or numbers"""
    if not coords or len(coords) < 3:
        return None
    
    # Normalize coordinates to a grid
    min_x = min(c[0] for c in coords)
    max_x = max(c[0] for c in coords)
    min_y = min(c[1] for c in coords)
    max_y = max(c[1] for c in coords)
    
    # Create grid mapping
    if max_x == min_x:
        scale_x = 1
    else:
        scale_x = 10 / (max_x - min_x)
    
    if max_y == min_y:
        scale_y = 1
    else:
        scale_y = 10 / (max_y - min_y)
    
    grid_coords = set()
    for x, y in coords:
        grid_x = round((x - min_x) * scale_x)
        grid_y = round((y - min_y) * scale_y)
        grid_coords.add((grid_x, grid_y))
    
    # Simple pattern templates for digits
    digit_patterns = {
        0: {(1,0), (2,0), (0,1), (3,1), (0,2), (3,2), (0,3), (3,3), (1,4), (2,4)},
        1: {(1,0), (0,1), (1,1), (1,2), (1,3), (0,4), (1,4), (2,4)},
        2: {(0,0), (1,0), (2,0), (3,1), (1,2), (2,2), (0,3), (0,4), (1,4), (2,4), (3,4)},
        3: {(0,0), (1,0), (2,0), (3,1), (1,2), (2,2), (3,3), (0,4), (1,4), (2,4)},
        4: {(0,0), (0,1), (3,0), (3,1), (0,2), (1,2), (2,2), (3,2), (3,3), (3,4)},
        5: {(0,0), (1,0), (2,0), (3,0), (0,1), (0,2), (1,2), (2,2), (3,3), (0,4), (1,4), (2,4)},
        6: {(1,0), (2,0), (0,1), (0,2), (1,2), (2,2), (0,3), (3,3), (1,4), (2,4)},
        7: {(0,0), (1,0), (2,0), (3,0), (3,1), (2,2), (1,3), (0,4)},
        8: {(1,0), (2,0), (0,1), (3,1), (1,2), (2,2), (0,3), (3,3), (1,4), (2,4)},
        9: {(1,0), (2,0), (0,1), (3,1), (1,2), (2,2), (3,2), (3,3), (1,4), (2,4)}
    }
    
    # Check for digit matches
    for digit, pattern in digit_patterns.items():
        if len(grid_coords.intersection(pattern)) >= len(pattern) * 0.6:  # 60% match
            return {"parameter": digit, "type": "digit", "confidence": 80}
    
    # Check for letter patterns (simplified)
    if len(grid_coords) <= 26:  # Could be a letter
        letter_index = len(grid_coords) - 1
        if 0 <= letter_index <= 25:
            letter = chr(ord('A') + letter_index)
            return {"parameter": letter, "type": "letter", "confidence": 60}
    
    return None


def detect_geometric_patterns(coords):
    """Detect geometric patterns in coordinates"""
    if not coords or len(coords) < 3:
        return None
    
    # Count unique x and y values
    x_vals = [c[0] for c in coords]
    y_vals = [c[1] for c in coords]
    unique_x = len(set(x_vals))
    unique_y = len(set(y_vals))
    
    # Check for line patterns
    if unique_x == 1:  # Vertical line
        return {"parameter": unique_y, "type": "vertical_line", "confidence": 70}
    elif unique_y == 1:  # Horizontal line
        return {"parameter": unique_x, "type": "horizontal_line", "confidence": 70}
    
    # Check for grid patterns
    if unique_x * unique_y == len(coords):  # Perfect grid
        return {"parameter": min(unique_x, unique_y), "type": "grid", "confidence": 75}
    
    # Check for simple count-based patterns
    coord_count = len(coords)
    if coord_count <= 26:
        return {"parameter": coord_count, "type": "count", "confidence": 50}
    
    return None


def analyze_coordinates_traditional(coords):
    """
    Traditional coordinate analysis for Challenge 2
    Implements outlier detection and pattern recognition
    """
    if not coords or len(coords) < 3:
        return {"error": "Insufficient coordinate data"}
    
    try:
        # Convert coordinates to numeric format
        numeric_coords = []
        for coord in coords:
            if isinstance(coord, (list, tuple)) and len(coord) >= 2:
                try:
                    x, y = float(coord[0]), float(coord[1])
                    numeric_coords.append((x, y))
                except (ValueError, TypeError):
                    continue
        
        if len(numeric_coords) < 3:
            return {"error": "Insufficient valid numeric coordinates"}
        
        # Step 1: Outlier Detection (Hint 2 - remove anomalies)
        filtered_coords = remove_outliers(numeric_coords)
        
        # Step 2: Pattern Recognition
        pattern_result = recognize_pattern(filtered_coords)
        
        return pattern_result
        
    except Exception as e:
        logger.error("Coordinate analysis error: %s", e)
        return {"error": f"Analysis failed: {str(e)}"}


def analyze_coordinates_enhanced(coords):
    """
    Enhanced coordinate analysis with better ASCII art pattern recognition
    """
    if not coords or len(coords) < 3:
        return {"error": "Insufficient coordinate data"}
    
    try:
        # Convert coordinates to numeric format
        numeric_coords = []
        for coord in coords:
            if isinstance(coord, (list, tuple)) and len(coord) >= 2:
                try:
                    x, y = float(coord[0]), float(coord[1])
                    numeric_coords.append((x, y))
                except (ValueError, TypeError):
                    continue
        
        if len(numeric_coords) < 3:
            return {"error": "Insufficient valid numeric coordinates"}
        
        # Enhanced pattern recognition for ASCII art
        result = recognize_ascii_pattern(numeric_coords)
        if result and "error" not in result:
            return result
        
        # Fallback to traditional analysis
        filtered_coords = remove_outliers(numeric_coords)
        pattern_result = recognize_pattern(filtered_coords)
        
        return pattern_result
        
    except Exception as e:
        logger.error("Enhanced coordinate analysis error: %s", e)
        return {"error": f"Enhanced analysis failed: {str(e)}"}


def recognize_ascii_pattern(coords):
    """
    Enhanced ASCII art pattern recognition
    """
    if len(coords) < 3:
        return {"error": "Insufficient coordinates for ASCII pattern recognition"}
    
    # Normalize coordinates to a standard grid
    min_x = min(c[0] for c in coords)
    max_x = max(c[0] for c in coords)
    min_y = min(c[1] for c in coords)
    max_y = max(c[1] for c in coords)
    
    # Create a larger grid for better pattern recognition
    grid_size = 20  # Smaller grid for better pattern matching
    if max_x - min_x > 0:
        scale_x = grid_size / (max_x - min_x)
    else:
        scale_x = 1
    if max_y - min_y > 0:
        scale_y = grid_size / (max_y - min_y)
    else:
        scale_y = 1
    
    # Map coordinates to grid
    grid_coords = []
    for x, y in coords:
        grid_x = int((x - min_x) * scale_x)
        grid_y = int((y - min_y) * scale_y)
        grid_coords.append((grid_x, grid_y))
    
    # Check for enhanced patterns
    patterns = check_enhanced_patterns(grid_coords)
    
    if patterns:
        # Return the most confident pattern
        best_pattern = max(patterns, key=lambda p: p.get('confidence', 0))
        return {
            "parameter": best_pattern['value'],
            "pattern_type": best_pattern['type'],
            "confidence": best_pattern['confidence'],
            "reasoning": f"Enhanced analysis found {best_pattern['type']} pattern"
        }
    
    # Try simple geometric analysis as fallback
    return analyze_simple_geometry(coords)


def check_enhanced_patterns(grid_coords):
    """
    Check for enhanced ASCII art patterns including numbers and symbols
    """
    patterns = []
    
    # Enhanced letter patterns (more detailed)
    letter_patterns = {
        'A': [(0, 4), (1, 3), (1, 5), (2, 2), (2, 6), (3, 1), (3, 7), (4, 0), (4, 8), (5, 1), (5, 7), (6, 2), (6, 6), (7, 3), (7, 5), (8, 4)],
        'B': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 4), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (3, 0), (3, 4), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        'C': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        'D': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 4), (2, 0), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        'E': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (1, 4), (2, 0), (2, 2), (2, 4), (3, 0), (3, 4), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        'F': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (2, 0), (2, 2), (3, 0), (4, 0)],
        'G': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 2), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3), (4, 4)],
        'H': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 2), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4)],
        'I': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 2), (3, 2), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        'J': [(0, 0), (0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        'K': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 1), (2, 3), (3, 0), (3, 4), (4, 0), (4, 4)],
        'L': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)],
        'M': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 1), (2, 2), (3, 1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        'N': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 1), (2, 2), (3, 3), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        'O': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        'P': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (2, 0), (2, 2), (3, 0), (4, 0)],
        'Q': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 4), (3, 0), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3), (4, 4)],
        'R': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (2, 0), (2, 2), (3, 0), (3, 3), (4, 0), (4, 4)],
        'S': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 2), (2, 2), (3, 2), (3, 4), (4, 1), (4, 2), (4, 3)],
        'T': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 2), (3, 2), (4, 2)],
        'U': [(0, 0), (0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (3, 4), (4, 0), (4, 1), (4, 2), (4, 3)],
        'V': [(0, 0), (0, 1), (1, 2), (2, 3), (3, 4), (4, 3), (5, 2), (6, 0), (6, 1)],
        'W': [(0, 0), (0, 1), (0, 2), (0, 3), (1, 4), (2, 2), (3, 4), (4, 0), (4, 1), (4, 2), (4, 3)],
        'X': [(0, 0), (0, 4), (1, 1), (1, 3), (2, 2), (3, 1), (3, 3), (4, 0), (4, 4)],
        'Y': [(0, 0), (0, 1), (1, 2), (2, 2), (3, 2), (4, 2)],
        'Z': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 3), (2, 2), (3, 1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)]
    }
    
    # Enhanced number patterns
    number_patterns = {
        '0': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        '1': [(0, 1), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, 1), (3, 1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        '2': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 3), (3, 2), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        '3': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 2), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        '4': [(0, 0), (0, 3), (1, 0), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (3, 3), (4, 3)],
        '5': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (1, 4), (2, 0), (2, 2), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        '6': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 2), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        '7': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 3), (2, 2), (3, 1), (4, 0)],
        '8': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 2), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        '9': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 2), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3), (4, 4)]
    }
    
    # Check letter patterns
    for letter, pattern in letter_patterns.items():
        confidence = calculate_pattern_confidence(grid_coords, pattern)
        if confidence > 0.3:  # Even lower threshold for better detection
            patterns.append({
                'value': letter,
                'type': 'letter',
                'confidence': int(confidence * 100)
            })
    
    # Check number patterns
    for number, pattern in number_patterns.items():
        confidence = calculate_pattern_confidence(grid_coords, pattern)
        if confidence > 0.3:  # Even lower threshold for better detection
            patterns.append({
                'value': int(number),
                'type': 'digit',
                'confidence': int(confidence * 100)
            })
    
    return patterns


def remove_outliers(coords, threshold=2.0):
    """
    Remove outliers using statistical methods
    Hint 2: "Certain coordinates stand apart—consider removing anomalies"
    """
    if len(coords) <= 3:
        return coords
    
    import statistics
    
    # Calculate distances from centroid
    centroid_x = statistics.mean([c[0] for c in coords])
    centroid_y = statistics.mean([c[1] for c in coords])
    
    distances = []
    for x, y in coords:
        dist = ((x - centroid_x) ** 2 + (y - centroid_y) ** 2) ** 0.5
        distances.append(dist)
    
    # Calculate threshold based on standard deviation
    mean_dist = statistics.mean(distances)
    std_dist = statistics.stdev(distances) if len(distances) > 1 else 0
    
    threshold_dist = mean_dist + threshold * std_dist
    
    # Filter out outliers
    filtered = []
    for i, (coord, dist) in enumerate(zip(coords, distances)):
        if dist <= threshold_dist:
            filtered.append(coord)
    
    logger.info(f"Removed {len(coords) - len(filtered)} outliers from {len(coords)} coordinates")
    return filtered if len(filtered) >= 3 else coords


def recognize_pattern(coords):
    """
    Recognize patterns in coordinates
    Hint 3: "The authentic coordinates, once isolated, collectively resemble something simple yet significant"
    """
    if len(coords) < 3:
        return {"error": "Insufficient coordinates for pattern recognition"}
    
    # Normalize coordinates to a grid
    min_x = min(c[0] for c in coords)
    max_x = max(c[0] for c in coords)
    min_y = min(c[1] for c in coords)
    max_y = max(c[1] for c in coords)
    
    # Create a grid representation
    grid_size = 20
    if max_x - min_x > 0:
        scale_x = grid_size / (max_x - min_x)
    else:
        scale_x = 1
    if max_y - min_y > 0:
        scale_y = grid_size / (max_y - min_y)
    else:
        scale_y = 1
    
    # Map coordinates to grid
    grid_coords = []
    for x, y in coords:
        grid_x = int((x - min_x) * scale_x)
        grid_y = int((y - min_y) * scale_y)
        grid_coords.append((grid_x, grid_y))
    
    # Check for common patterns
    patterns = check_common_patterns(grid_coords)
    
    if patterns:
        # Return the most confident pattern
        best_pattern = max(patterns, key=lambda p: p.get('confidence', 0))
        return {
            "parameter": best_pattern['value'],
            "pattern_type": best_pattern['type'],
            "confidence": best_pattern['confidence'],
            "reasoning": f"Traditional analysis found {best_pattern['type']} pattern"
        }
    
    # If no clear pattern found, try simple fallback based on coordinate count
    coord_count = len(coords)
    if coord_count <= 9:  # Single digit
        return {
            "parameter": coord_count,
            "pattern_type": "count",
            "confidence": 60,
            "reasoning": f"Coordinate count suggests parameter: {coord_count}"
        }
    elif coord_count <= 26:  # Could be a letter (A=1, B=2, etc.)
        letter = chr(ord('A') + coord_count - 1)
        return {
            "parameter": letter,
            "pattern_type": "letter_from_count",
            "confidence": 50,
            "reasoning": f"Coordinate count {coord_count} maps to letter: {letter}"
        }
    
    # If no clear pattern found, try simple geometric analysis
    return analyze_geometry(coords)


def check_common_patterns(grid_coords):
    """
    Check for common ASCII art patterns in coordinates
    """
    patterns = []
    
    # Check for letter patterns
    letter_patterns = {
        'A': [(0, 4), (1, 3), (1, 5), (2, 2), (2, 6), (3, 1), (3, 7), (4, 0), (4, 8)],
        'B': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 4), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],
        'C': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        'D': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 4), (2, 0), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        'E': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (1, 4), (2, 0), (2, 2), (2, 4), (3, 0), (3, 4), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        'F': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (2, 0), (2, 2), (3, 0), (4, 0)],
        'G': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 2), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3), (4, 4)],
        'H': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 2), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4)],
        'I': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 2), (3, 2), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        'J': [(0, 0), (0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        'K': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 1), (2, 3), (3, 0), (3, 4), (4, 0), (4, 4)],
        'L': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)],
        'M': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 1), (2, 2), (3, 1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        'N': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 1), (2, 2), (3, 3), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        'O': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        'P': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (2, 0), (2, 2), (3, 0), (4, 0)],
        'Q': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 4), (3, 0), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3), (4, 4)],
        'R': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (2, 0), (2, 2), (3, 0), (3, 3), (4, 0), (4, 4)],
        'S': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 2), (2, 2), (3, 2), (3, 4), (4, 1), (4, 2), (4, 3)],
        'T': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 2), (3, 2), (4, 2)],
        'U': [(0, 0), (0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (3, 4), (4, 0), (4, 1), (4, 2), (4, 3)],
        'V': [(0, 0), (0, 1), (1, 2), (2, 3), (3, 4), (4, 3), (5, 2), (6, 0), (6, 1)],
        'W': [(0, 0), (0, 1), (0, 2), (0, 3), (1, 4), (2, 2), (3, 4), (4, 0), (4, 1), (4, 2), (4, 3)],
        'X': [(0, 0), (0, 4), (1, 1), (1, 3), (2, 2), (3, 1), (3, 3), (4, 0), (4, 4)],
        'Y': [(0, 0), (0, 1), (1, 2), (2, 2), (3, 2), (4, 2)],
        'Z': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 3), (2, 2), (3, 1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)]
    }
    
    # Check for number patterns
    number_patterns = {
        '0': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        '1': [(0, 1), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, 1), (3, 1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        '2': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 3), (3, 2), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
        '3': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 2), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        '4': [(0, 0), (0, 3), (1, 0), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (3, 3), (4, 3)],
        '5': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (1, 4), (2, 0), (2, 2), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        '6': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 2), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        '7': [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 3), (2, 2), (3, 1), (4, 0)],
        '8': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 2), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3)],
        '9': [(0, 1), (0, 2), (0, 3), (1, 0), (1, 4), (2, 0), (2, 2), (2, 4), (3, 0), (3, 4), (4, 1), (4, 2), (4, 3), (4, 4)]
    }
    
    # Check letter patterns
    for letter, pattern in letter_patterns.items():
        confidence = calculate_pattern_confidence(grid_coords, pattern)
        if confidence > 0.4:  # Lower threshold for better detection
            patterns.append({
                'value': letter,
                'type': 'letter',
                'confidence': int(confidence * 100)
            })
    
    # Check number patterns
    for number, pattern in number_patterns.items():
        confidence = calculate_pattern_confidence(grid_coords, pattern)
        if confidence > 0.4:  # Lower threshold for better detection
            patterns.append({
                'value': int(number),
                'type': 'digit',
                'confidence': int(confidence * 100)
            })
    
    return patterns


def calculate_pattern_confidence(coords, pattern):
    """
    Calculate confidence score for a pattern match
    """
    if not coords or not pattern:
        return 0
    
    # Normalize pattern to match coordinate scale
    pattern_coords = set(pattern)
    coord_set = set(coords)
    
    # Calculate overlap
    matches = len(pattern_coords.intersection(coord_set))
    total_pattern = len(pattern_coords)
    total_coords = len(coord_set)
    
    # Confidence based on matches and coverage
    if total_pattern == 0:
        return 0
    
    match_ratio = matches / total_pattern
    coverage_ratio = matches / total_coords if total_coords > 0 else 0
    
    # Weighted confidence (more weight on match ratio)
    confidence = (match_ratio * 0.7) + (coverage_ratio * 0.3)
    
    return min(confidence, 1.0)


def analyze_simple_geometry(coords):
    """
    Simple geometric analysis for coordinate patterns
    """
    if len(coords) < 3:
        return {"error": "Insufficient coordinates for geometric analysis"}
    
    # Calculate basic geometric properties
    import statistics
    
    x_coords = [c[0] for c in coords]
    y_coords = [c[1] for c in coords]
    
    # Check if coordinates form a line
    if len(set(x_coords)) == 1:  # Vertical line
        return {
            "parameter": "VERTICAL_LINE",
            "pattern_type": "line",
            "confidence": 80,
            "reasoning": "Coordinates form a vertical line"
        }
    elif len(set(y_coords)) == 1:  # Horizontal line
        return {
            "parameter": "HORIZONTAL_LINE", 
            "pattern_type": "line",
            "confidence": 80,
            "reasoning": "Coordinates form a horizontal line"
        }
    
    # Check for clustering
    centroid_x = statistics.mean(x_coords)
    centroid_y = statistics.mean(y_coords)
    
    distances = [((c[0] - centroid_x) ** 2 + (c[1] - centroid_y) ** 2) ** 0.5 for c in coords]
    avg_distance = statistics.mean(distances)
    
    if avg_distance < 1.0:  # Tight cluster
        return {
            "parameter": "CLUSTER",
            "pattern_type": "cluster",
            "confidence": 70,
            "reasoning": f"Coordinates form a tight cluster (avg distance: {avg_distance:.2f})"
        }
    
    # Check for simple patterns like numbers
    # Try to identify if coordinates form a simple number pattern
    if len(coords) <= 10:  # Small number of coordinates might form a digit
        # Check if coordinates form a simple shape that could be a number
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        # Check for rectangular patterns
        if max_x - min_x > 0 and max_y - min_y > 0:
            aspect_ratio = (max_x - min_x) / (max_y - min_y)
            if 0.5 < aspect_ratio < 2.0:  # Roughly square or rectangular
                # This could be a simple number or letter
                return {
                    "parameter": len(coords),
                    "pattern_type": "simple_shape",
                    "confidence": 60,
                    "reasoning": f"Coordinates form a simple shape with {len(coords)} points"
                }
    
    # Default fallback - try to find a more meaningful pattern
    # Check if coordinates form a simple geometric pattern
    if len(coords) >= 3:
        # Try to find if coordinates form a recognizable shape
        x_coords = [c[0] for c in coords]
        y_coords = [c[1] for c in coords]
        
        # Check for diagonal patterns
        if len(set(x_coords)) == len(coords) and len(set(y_coords)) == len(coords):
            # All coordinates are unique - might form a diagonal or specific pattern
            return {
                "parameter": "DIAGONAL",
                "pattern_type": "diagonal",
                "confidence": 60,
                "reasoning": "Coordinates form a diagonal pattern"
            }
        
        # Check for circular patterns
        centroid_x = statistics.mean(x_coords)
        centroid_y = statistics.mean(y_coords)
        distances = [((c[0] - centroid_x) ** 2 + (c[1] - centroid_y) ** 2) ** 0.5 for c in coords]
        if len(set(round(d, 2) for d in distances)) <= 2:  # Most distances are similar
            return {
                "parameter": "CIRCLE",
                "pattern_type": "circle",
                "confidence": 60,
                "reasoning": "Coordinates form a circular pattern"
            }
    
    # Last resort - return coordinate count but with lower confidence
    return {
        "parameter": len(coords),
        "pattern_type": "count",
        "confidence": 30,
        "reasoning": f"Fallback to coordinate count: {len(coords)}"
    }


def analyze_geometry(coords):
    """
    Fallback geometric analysis
    """
    if len(coords) < 3:
        return {"error": "Insufficient coordinates for geometric analysis"}
    
    # Calculate basic geometric properties
    import statistics
    
    x_coords = [c[0] for c in coords]
    y_coords = [c[1] for c in coords]
    
    # Check if coordinates form a line
    if len(set(x_coords)) == 1:  # Vertical line
        return {
            "parameter": "VERTICAL_LINE",
            "pattern_type": "line",
            "confidence": 80,
            "reasoning": "Coordinates form a vertical line"
        }
    elif len(set(y_coords)) == 1:  # Horizontal line
        return {
            "parameter": "HORIZONTAL_LINE", 
            "pattern_type": "line",
            "confidence": 80,
            "reasoning": "Coordinates form a horizontal line"
        }
    
    # Check for clustering
    centroid_x = statistics.mean(x_coords)
    centroid_y = statistics.mean(y_coords)
    
    distances = [((c[0] - centroid_x) ** 2 + (c[1] - centroid_y) ** 2) ** 0.5 for c in coords]
    avg_distance = statistics.mean(distances)
    
    if avg_distance < 1.0:  # Tight cluster
        return {
            "parameter": "CLUSTER",
            "pattern_type": "cluster",
            "confidence": 70,
            "reasoning": f"Coordinates form a tight cluster (avg distance: {avg_distance:.2f})"
        }
    
    # Default fallback
    return {
        "parameter": len(coords),
        "pattern_type": "count",
        "confidence": 50,
        "reasoning": f"Returning coordinate count: {len(coords)}"
    }


def decrypt_final_message_with_components(encrypted_message, challenge_one_result, challenge_two_result, challenge_three_result):
    """
    Decrypt the final message using components from previous challenges
    """
    if not isinstance(encrypted_message, str):
        return {
            "error": "Challenge four data must be a string message",
            "received_type": type(encrypted_message).__name__
        }
    
    # Extract key components from previous challenges
    key_components = extract_key_components(challenge_one_result, challenge_two_result, challenge_three_result)
    
    # Try various decryption methods using the extracted components
    decryption_attempts = {}
    
    # Method 1: Caesar cipher with different shifts
    for shift in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]:
        decryption_attempts[f"caesar_{shift}"] = caesar_decrypt(encrypted_message, shift)
    
    # Method 2: Atbash cipher
    decryption_attempts["atbash"] = atbash_decrypt(encrypted_message)
    
    # Method 3: Reverse the string
    decryption_attempts["reverse"] = reverse_decrypt(encrypted_message)
    
    # Method 4: Vigenère cipher using extracted keys
    for key in key_components.get("potential_keys", []):
        if isinstance(key, str) and len(key) > 0:
            decryption_attempts[f"vigenere_{key}"] = vigenere_decrypt(encrypted_message, key)
    
    # Method 5: XOR cipher using numeric components
    for num_key in key_components.get("numeric_keys", []):
        if isinstance(num_key, (int, float)) and num_key > 0:
            decryption_attempts[f"xor_{int(num_key)}"] = xor_decrypt(encrypted_message, int(num_key))
    
    # Method 6: Rail fence cipher with different rail counts
    for rails in [2, 3, 4, 5, 6]:
        decryption_attempts[f"railfence_{rails}"] = decrypt_railfence(encrypted_message, rails)
    
    # Method 7: Keyword substitution using extracted keywords
    for keyword in key_components.get("keywords", []):
        if isinstance(keyword, str) and len(keyword) > 0:
            decryption_attempts[f"keyword_{keyword}"] = decrypt_keyword(encrypted_message, keyword)
    
    # Look for meaningful decrypted text
    meaningful_results = []
    for method, result in decryption_attempts.items():
        # Check if result contains common words or patterns
        if any(word in result.upper() for word in config.MEANINGFUL_WORDS):
            meaningful_results.append((method, result))
    
    if meaningful_results:
        # Return the most likely decrypted message
        return {
            "decrypted_message": meaningful_results[0][1],
            "decryption_method": meaningful_results[0][0],
            "key_components_used": key_components,
            "all_attempts": decryption_attempts
        }
    else:
        return {
            "decrypted_message": "Unable to decrypt - no meaningful patterns found",
            "key_components_used": key_components,
            "all_attempts": decryption_attempts
        }


def extract_key_components(challenge_one_result, challenge_two_result, challenge_three_result):
    """
    Extract potential keys and components from previous challenge results
    """
    components = {
        "potential_keys": [],
        "numeric_keys": [],
        "keywords": [],
        "text_components": []
    }
    
    # Extract from Challenge 1 (reverse obfuscation result)
    if challenge_one_result and isinstance(challenge_one_result, str):
        components["text_components"].append(challenge_one_result)
        # Try to extract potential keys from the text
        words = challenge_one_result.split()
        for word in words:
            if len(word) >= 3 and word.isalpha():
                components["potential_keys"].append(word.upper())
                components["keywords"].append(word.upper())
    
    # Extract from Challenge 2 (coordinate analysis result)
    if challenge_two_result:
        if isinstance(challenge_two_result, dict):
            param = challenge_two_result.get("parameter")
            if param is not None:
                if isinstance(param, (int, float)):
                    components["numeric_keys"].append(param)
                elif isinstance(param, str):
                    components["text_components"].append(param)
                    if param.isalpha() and len(param) >= 2:
                        components["potential_keys"].append(param.upper())
        elif isinstance(challenge_two_result, str):
            # Try to parse JSON response
            try:
                parsed = json.loads(challenge_two_result)
                if isinstance(parsed, dict):
                    param = parsed.get("parameter")
                    if param is not None:
                        if isinstance(param, (int, float)):
                            components["numeric_keys"].append(param)
                        elif isinstance(param, str):
                            components["text_components"].append(param)
                            if param.isalpha() and len(param) >= 2:
                                components["potential_keys"].append(param.upper())
            except json.JSONDecodeError:
                # If not JSON, treat as text
                components["text_components"].append(challenge_two_result)
    
    # Extract from Challenge 3 (cipher decryption result)
    if challenge_three_result and isinstance(challenge_three_result, dict):
        decrypted_text = challenge_three_result.get("decrypted_text", "")
        if decrypted_text and isinstance(decrypted_text, str):
            components["text_components"].append(decrypted_text)
            # Extract potential keys from decrypted text
            words = decrypted_text.split()
            for word in words:
                if len(word) >= 3 and word.isalpha():
                    components["potential_keys"].append(word.upper())
                    components["keywords"].append(word.upper())
    
    # Remove duplicates
    components["potential_keys"] = list(set(components["potential_keys"]))
    components["keywords"] = list(set(components["keywords"]))
    components["numeric_keys"] = list(set(components["numeric_keys"]))
    
    return components


def caesar_decrypt(text, shift):
    """Caesar cipher decryption"""
    result = ""
    for char in text.upper():
        if char.isalpha():
            result += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
        else:
            result += char
    return result


def atbash_decrypt(text):
    """Atbash cipher decryption (A=Z, B=Y, etc.)"""
    result = ""
    for char in text.upper():
        if char.isalpha():
            result += chr(ord('Z') - (ord(char) - ord('A')))
        else:
            result += char
    return result


def reverse_decrypt(text):
    """Reverse string decryption"""
    return text[::-1]


def vigenere_decrypt(text, key):
    """Vigenère cipher decryption"""
    result = ""
    key_index = 0
    for char in text.upper():
        if char.isalpha():
            shift = ord(key[key_index % len(key)].upper()) - ord('A')
            decrypted_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            result += decrypted_char
            key_index += 1
        else:
            result += char
    return result


def xor_decrypt(text, key):
    """XOR cipher decryption"""
    result = ""
    for i, char in enumerate(text):
        result += chr(ord(char) ^ (key % 256))
    return result


def decrypt_railfence(text, rails):
    """Rail fence cipher decryption"""
    if not text or rails <= 0:
        return ""
    
    # Create the rail pattern
    rail_pattern = []
    for i in range(rails):
        rail_pattern.append([])
    
    # Calculate the pattern for reading
    rail_lengths = [0] * rails
    direction = 1
    rail = 0
    
    for i in range(len(text)):
        rail_lengths[rail] += 1
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction = -direction
    
    # Fill the rails
    text_index = 0
    for rail in range(rails):
        for pos in range(rail_lengths[rail]):
            rail_pattern[rail].append(text[text_index])
            text_index += 1
    
    # Read the decrypted text
    result = ""
    direction = 1
    rail = 0
    rail_positions = [0] * rails
    
    for i in range(len(text)):
        result += rail_pattern[rail][rail_positions[rail]]
        rail_positions[rail] += 1
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction = -direction
    
    return result


def decrypt_keyword(text, keyword):
    """Keyword substitution cipher decryption"""
    # Create cipher alphabet with keyword first, removing duplicates
    cipher_alphabet = ""
    seen = set()
    for char in keyword.upper():
        if char.isalpha() and char not in seen:
            cipher_alphabet += char
            seen.add(char)
    
    # Add remaining alphabet characters not in keyword
    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if char not in seen:
            cipher_alphabet += char
    
    # Create substitution mapping (cipher alphabet maps to normal alphabet)
    substitution = {}
    normal_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, cipher_char in enumerate(cipher_alphabet):
        if i < len(normal_alphabet):
            substitution[cipher_char] = normal_alphabet[i]
    
    # Decrypt the text
    result = ""
    for char in text.upper():
        if char in substitution:
            result += substitution[char]
        else:
            result += char
    
    return result


def decrypt_polybius(text):
    """Polybius square cipher decryption (5x5 grid, I/J combined)"""
    # Create Polybius square
    polybius_square = [
        ['A', 'B', 'C', 'D', 'E'],
        ['F', 'G', 'H', 'I', 'K'],  # I and J share position
        ['L', 'M', 'N', 'O', 'P'],
        ['Q', 'R', 'S', 'T', 'U'],
        ['V', 'W', 'X', 'Y', 'Z']
    ]
    
    # Create reverse mapping
    reverse_map = {}
    for row in range(5):
        for col in range(5):
            reverse_map[f"{row+1}{col+1}"] = polybius_square[row][col]
    
    # Decrypt pairs of digits
    result = ""
    for i in range(0, len(text), 2):
        if i + 1 < len(text):
            pair = text[i:i+2]
            if pair in reverse_map:
                result += reverse_map[pair]
            else:
                result += pair
        else:
            result += text[i]
    
    return result


@app.route('/operation-safeguard', methods=['POST'])
def operation_safeguard():
    """    Expects JSON in the format:
    {
      "challenge_one": {
        "transformations": "[encode_mirror_alphabet(x), double_consonants(x), mirror_words(x), swap_pairs(x), encode_index_parity(x)]",
        "transformed_encrypted_word": "<REDACTED>"
      },
      "challenge_two": [
        ["<LAT>", "<LONG>"],
        ["<LAT>", "<LONG>"],
        ["<LAT>", "<LONG>"],
        ["<LAT>", "<LONG>"]
      ],
      "challenge_three": "PRIORITY: HIGH | SOURCE: C2_ALPHA | CIPHER_TYPE: ROTATION_CIPHER | SESSION_ID: SES_445 | CLASSIFICATION: OPERATION_KEY | ENCRYPTED_PAYLOAD: SVERJNYY | ENTRY_ID: LOG_3646 | TIMESTAMP: 2025-01-11 00:42:34 UTC"
    }
    
    Returns:
    {
      "challenge_one": "<value_from_challenge_1>",
      "challenge_two": "<value_from_challenge_2>",
      "challenge_three": "<value_from_challenge_3>",
      "challenge_four": "<final_decrypted_value>"
    }
    """
    try:
        payload = request.get_json(force=True)
        
        if not isinstance(payload, dict):
            return jsonify({
                "error": "Invalid payload format",
                "expected": "JSON object with challenge_one, challenge_two, challenge_three keys",
                "received": f"{type(payload).__name__}"
            }), 400
        
        # Extract challenge data with proper validation
        challenge_one_data = payload.get("challenge_one", {})
        challenge_two_data = payload.get("challenge_two", [])
        challenge_three_data = payload.get("challenge_three", "")
        challenge_four_data = payload.get("challenge_four", "")
        
        # Validate required fields
        if not challenge_one_data:
            return jsonify({"error": "challenge_one is required"}), 400
        if not challenge_two_data:
            return jsonify({"error": "challenge_two is required"}), 400
        if not challenge_three_data:
            return jsonify({"error": "challenge_three is required"}), 400
        
    except Exception as e:
        logger.error("Failed to parse JSON payload: %s", e)
        return jsonify({
            "error": "Failed to parse JSON payload",
            "details": str(e)
        }), 400

    # Challenge 1 - Reverse Obfuscation Analysis
    challenge_one_out = None
    
    # Extract transformations and transformed word from challenge_one_data
    transformations = challenge_one_data.get("transformations", "")
    transformed_word = challenge_one_data.get("transformed_encrypted_word", "")
    
    if transformations and transformed_word:
        # Robust transformation and reverse transformation functions
        def mirror_words(x):
            """Reverse each word in the sentence, keeping word order"""
            if not x:
                return x
            words = x.split(' ')
            return ' '.join(word[::-1] for word in words)
        
        def encode_mirror_alphabet(x):
            """Replace each letter with its mirror in the alphabet (a ↔️ z, b ↔️ y, ..., A ↔️ Z)"""
            if not x:
                return x
            result = ""
            for char in x:
                if char.isalpha():
                    if char.islower():
                        result += chr(ord('z') - (ord(char) - ord('a')))
                    else:
                        result += chr(ord('Z') - (ord(char) - ord('A')))
                else:
                    result += char
            return result
        
        def toggle_case(x):
            """Switch uppercase letters to lowercase and vice versa"""
            if not x:
                return x
            return x.swapcase()
        
        def swap_pairs(x):
            """Swap characters in pairs within each word; if odd length, last char stays"""
            if not x:
                return x
            words = x.split(' ')
            result_words = []
            for word in words:
                if len(word) <= 1:
                    result_words.append(word)
                else:
                    chars = list(word)
                    for i in range(0, len(chars) - 1, 2):
                        chars[i], chars[i + 1] = chars[i + 1], chars[i]
                    result_words.append(''.join(chars))
            return ' '.join(result_words)
        
        def encode_index_parity(x):
            """Rearrange each word: even indices first, then odd indices"""
            if not x:
                return x
            words = x.split(' ')
            result_words = []
            for word in words:
                if len(word) <= 1:
                    result_words.append(word)
                else:
                    even_chars = [word[i] for i in range(0, len(word), 2)]
                    odd_chars = [word[i] for i in range(1, len(word), 2)]
                    result_words.append(''.join(even_chars + odd_chars))
            return ' '.join(result_words)
        
        def double_consonants(x):
            """Double every consonant (letters other than a, e, i, o, u)"""
            if not x:
                return x
            vowels = set('aeiouAEIOU')
            result = ""
            for char in x:
                result += char
                if char.isalpha() and char not in vowels:
                    result += char
            return result
        
        # Reverse transformation functions
        def reverse_double_consonants(x):
            """Reverse of double_consonants - remove doubled consonants"""
            if not x:
                return x
            vowels = set('aeiouAEIOU')
            result = ""
            i = 0
            while i < len(x):
                result += x[i]
                # If current char is a consonant and next char is the same, skip the duplicate
                if (i + 1 < len(x) and 
                    x[i] == x[i + 1] and 
                    x[i].isalpha() and 
                    x[i] not in vowels):
                    i += 1  # Skip the doubled consonant
                i += 1
            return result
        
        def reverse_encode_index_parity(x):
            """Reverse of encode_index_parity - reconstruct original positions"""
            if not x:
                return x
            words = x.split(' ')
            result_words = []
            for word in words:
                if len(word) <= 1:
                    result_words.append(word)
                else:
                    # Calculate original even and odd positions
                    original_len = len(word)
                    even_count = (original_len + 1) // 2
                    
                    even_chars = word[:even_count]
                    odd_chars = word[even_count:]
                    
                    # Reconstruct by interleaving
                    result_chars = [''] * original_len
                    for i, char in enumerate(even_chars):
                        result_chars[i * 2] = char
                    for i, char in enumerate(odd_chars):
                        if i * 2 + 1 < original_len:
                            result_chars[i * 2 + 1] = char
                    
                    result_words.append(''.join(result_chars))
            return ' '.join(result_words)
        
        # Extract and parse transformations
        transformations_str = str(transformations) if transformations else ""
        
        # Handle different transformation formats
        import re
        function_matches = []
        
        # Try different regex patterns for function extraction
        patterns = [
            r'(\w+)\s*\(\s*x\s*\)',  # Standard format: function(x)
            r'(\w+)\s*\(',           # Just function name with opening paren
            r'(\w+)(?=\s*[,\]\)])',  # Function name followed by comma or bracket
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, transformations_str, re.IGNORECASE)
            if matches:
                function_matches = matches
                break
        
        # If regex fails, try simple splitting
        if not function_matches:
            # Remove brackets and split by comma
            clean_str = transformations_str.replace('[', '').replace(']', '').replace('(x)', '')
            potential_functions = [f.strip() for f in clean_str.split(',')]
            function_matches = [f for f in potential_functions if f and f.replace('_', '').isalpha()]
        
        # Create mapping of function names to reverse functions
        reverse_functions = {
            'mirror_words': mirror_words,  # Self-inverse
            'encode_mirror_alphabet': encode_mirror_alphabet,  # Self-inverse
            'toggle_case': toggle_case,  # Self-inverse
            'swap_pairs': swap_pairs,  # Self-inverse
            'encode_index_parity': reverse_encode_index_parity,
            'double_consonants': reverse_double_consonants
        }
        
        # Apply reverse transformations in opposite order
        current_word = str(transformed_word)
        logger.info(f"Starting with: {current_word}")
        logger.info(f"Functions to reverse: {function_matches}")
        
        for func_name in reversed(function_matches):
            func_name = func_name.strip().lower()
            if func_name in reverse_functions:
                prev_word = current_word
                current_word = reverse_functions[func_name](current_word)
                logger.info(f"Applied reverse {func_name}: '{prev_word}' -> '{current_word}'")
        
        challenge_one_out = current_word
    else:
        # Fallback to AI-powered analysis if traditional methods fail
        if ENABLE_AI_FALLBACK and (transformations or transformed_word):
            try:
                transformations_str = str(transformations) if transformations else ""
                transformed_word_str = str(transformed_word) if transformed_word else ""
                
                prompt = f"""
You are a cryptanalysis expert specializing in text transformation reversal.

TASK: Reverse the transformations applied to recover the original text.

TRANSFORMATIONS APPLIED: {transformations_str}
TRANSFORMED TEXT: {transformed_word_str}

TRANSFORMATION FUNCTIONS (apply in REVERSE order):
1. mirror_words(x) - Reverse each word individually (self-inverse)
2. encode_mirror_alphabet(x) - Replace letters with alphabet mirror a↔z, b↔y (self-inverse)
3. toggle_case(x) - Switch case of all letters (self-inverse)
4. swap_pairs(x) - Swap characters in pairs within words (self-inverse)
5. encode_index_parity(x) - Rearrange: even indices first, then odd indices
6. double_consonants(x) - Double every consonant letter

REVERSAL RULES:
- Apply transformations in REVERSE ORDER
- For encode_index_parity: split word, take first half as even positions, second half as odd positions, then interleave
- For double_consonants: remove duplicate consonants (but keep vowels unchanged)
- Other functions are self-inverse

EXAMPLE:
If transformations = "[double_consonants(x), swap_pairs(x)]" and text = "HHEELLLLOO"
1. Reverse double_consonants: "HHEELLLLOO" → "HELLO" (remove doubled consonants L, L)
2. Reverse swap_pairs: "HELLO" → "EHLLO" (swap HE → EH, LL stays, O stays)

Respond with ONLY the original decrypted text, no explanations.
"""
                
                data = {
                    "model": OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a skilled cryptanalyst specializing in text obfuscation reversal."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": OPENAI_TEMPERATURE
                }
                resp = requests.post(OPENAI_URL, headers=HEADERS, data=json.dumps(data))
                if resp.status_code == 200:
                    content = resp.json()["choices"][0]["message"]["content"].strip()
                    challenge_one_out = content
                    logger.info("Challenge 1 AI fallback successful: %s", content)
                else:
                    logger.error("Challenge 1 AI fallback failed: %s", resp.text)
                    challenge_one_out = str(transformed_word) if transformed_word else "AI fallback failed"
            except Exception as e:
                logger.error("Challenge 1 AI fallback exception: %s", e)
                challenge_one_out = str(transformed_word) if transformed_word else "AI fallback exception"
        else:
            challenge_one_out = str(transformed_word) if transformed_word else "Invalid challenge_one data format"

    # Challenge 2 (coordinate analysis with enhanced pattern recognition)
    coords = challenge_two_data
    challenge_two_out = None
    if coords:
        try:
            # Convert all coordinates to float tuples
            numeric_coords = []
            for coord in coords:
                if isinstance(coord, (list, tuple)) and len(coord) >= 2:
                    try:
                        x, y = float(coord[0]), float(coord[1])
                        numeric_coords.append((x, y))
                    except (ValueError, TypeError):
                        continue
            
            if len(numeric_coords) < 3:
                challenge_two_out = str(len(coords))
            else:
                # Try multiple analysis approaches
                result = None
                
                # Method 1: Try to detect ASCII art patterns
                result = detect_ascii_patterns(numeric_coords)
                
                if not result:
                    # Method 2: Try geometric patterns
                    result = detect_geometric_patterns(numeric_coords)
                
                if not result:
                    # Method 3: Count-based analysis
                    result = len(numeric_coords)
                
                if not result:
                    # Method 4: AI fallback
                    if ENABLE_AI_FALLBACK:
                        try:
                            coords_text = "\n".join(f"({c[0]}, {c[1]})" for c in numeric_coords)
                            
                            prompt = f"""
You are an expert in spatial pattern recognition and cryptanalysis.

TASK: Analyze these coordinates to find a hidden pattern or parameter.

COORDINATES:
{coords_text}

ANALYSIS STEPS:
1. Look for ASCII art patterns (letters A-Z, digits 0-9)
2. Check for geometric shapes or arrangements
3. Identify any obvious outliers to remove
4. Consider the coordinate count itself as a parameter

COMMON PATTERNS:
- Coordinates forming letters/numbers in ASCII art style
- Grid patterns indicating dimensions
- Clustered points suggesting groupings
- Simple count-based encoding

OUTPUT: Respond with ONLY the parameter value (single number, letter, or short word). Examples: "5", "A", "HELLO"
"""
                            
                            data = {
                                "model": OPENAI_MODEL,
                                "messages": [
                                    {"role": "system", "content": "You are a pattern recognition expert."},
                                    {"role": "user", "content": prompt}
                                ],
                                "temperature": OPENAI_TEMPERATURE
                            }
                            resp = requests.post(OPENAI_URL, headers=HEADERS, data=json.dumps(data))
                            if resp.status_code == 200:
                                ai_result = resp.json()["choices"][0]["message"]["content"].strip()
                                result = ai_result
                                logger.info("Challenge 2 AI fallback successful: %s", ai_result)
                            else:
                                result = len(numeric_coords)
                        except Exception as e:
                            logger.error("Challenge 2 AI fallback exception: %s", e)
                            result = len(numeric_coords)
                    else:
                        result = len(numeric_coords)
                
                # Extract parameter from result
                if isinstance(result, dict) and "parameter" in result:
                    challenge_two_out = str(result["parameter"])
                else:
                    challenge_two_out = str(result)
                    
        except Exception as e:
            logger.error(f"Challenge 2 analysis error: {e}")
            challenge_two_out = str(len(coords)) if coords else "0"

    # Challenge 3 - Operational Intelligence Extraction
    log_string = challenge_three_data
    challenge_three_out = None
    
    if log_string:
        # Parse log entry to extract cipher type and encrypted payload
        import re
        
        cipher_type = ""
        encrypted_payload = ""
        
        # Enhanced patterns to extract cipher type and payload
        cipher_patterns = [
            r'CIPHER_TYPE:\s*([A-Z_]+)',
            r'cipher_type:\s*([A-Za-z_]+)',
            r'Cipher:\s*([A-Za-z_]+)',
            r'Type:\s*([A-Za-z_]+)',
            r'cipher\s*=\s*([A-Za-z_]+)',
            r'type\s*=\s*([A-Za-z_]+)',
            r'\b(RAILFENCE|KEYWORD|POLYBIUS|ROTATION_CIPHER|CAESAR|ATBASH|VIGENERE|SUBSTITUTION)\b'
        ]
        
        payload_patterns = [
            r'ENCRYPTED_PAYLOAD:\s*([A-Za-z0-9]+)',
            r'encrypted_payload:\s*([A-Za-z0-9]+)',
            r'Payload:\s*([A-Za-z0-9]+)',
            r'Data:\s*([A-Za-z0-9]+)',
            r'Text:\s*([A-Za-z0-9]+)',
            r'payload\s*=\s*([A-Za-z0-9]+)',
            r'data\s*=\s*([A-Za-z0-9]+)',
            r'text\s*=\s*([A-Za-z0-9]+)'
        ]
        
        # Try to find cipher type
        for pattern in cipher_patterns:
            match = re.search(pattern, log_string, re.IGNORECASE)
            if match:
                cipher_type = match.group(1).upper()
                break
        
        # Try to find encrypted payload
        for pattern in payload_patterns:
            match = re.search(pattern, log_string, re.IGNORECASE)
            if match:
                encrypted_payload = match.group(1).upper()
                break
        
        # If no payload found by patterns, look for any sequence that could be encrypted data
        if not encrypted_payload:
            # Find all sequences of 4+ alphanumeric characters
            candidates = re.findall(r'\b([A-Za-z]{4,})\b', log_string)
            if candidates:
                # Choose the longest candidate, preferring uppercase sequences
                encrypted_payload = max(candidates, key=lambda x: (len(x), x.isupper())).upper()
        
        logger.info(f"Extracted cipher_type: {cipher_type}, payload: {encrypted_payload}")
        
        if cipher_type and encrypted_payload:
            # Decrypt based on cipher type
            decrypted_text = ""
            
            if cipher_type == "RAILFENCE":
                decrypted_text = decrypt_railfence(encrypted_payload, config.DEFAULT_RAILFENCE_RAILS)
            elif cipher_type == "KEYWORD":
                decrypted_text = decrypt_keyword(encrypted_payload, config.DEFAULT_KEYWORD)
            elif cipher_type == "POLYBIUS":
                decrypted_text = decrypt_polybius(encrypted_payload)
            elif cipher_type in ["ROTATION_CIPHER", "CAESAR"]:
                # Handle rotation cipher with improved scoring
                best_result = ""
                best_score = 0
                
                for shift in [13, 1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]:
                    candidate = ""
                    for char in encrypted_payload:
                        if char.isalpha():
                            candidate += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                        else:
                            candidate += char
                    
                    # Score the candidate
                    score = 0
                    
                    # Check for common English words
                    common_words = ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HAD", 
                                  "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "GET", "HAS", "HIM", "HIS", 
                                  "HOW", "MAN", "NEW", "NOW", "OLD", "SEE", "TWO", "WAY", "WHO", "BOY", 
                                  "DID", "ITS", "LET", "PUT", "SAY", "SHE", "TOO", "USE", "ATTACK", 
                                  "MISSION", "TARGET", "SECURE", "AGENT", "OPERATION", "INTEL", "STATUS", 
                                  "REPORT", "CONFIRM", "COMPLETE"]
                    for word in common_words:
                        if word in candidate:
                            score += len(word) * 2
                    
                    # Prefer reasonable letter frequencies
                    for letter in "ETAOIN":
                        score += candidate.count(letter)
                    
                    if score > best_score or (score >= best_score and shift == 13):
                        best_result = candidate
                        best_score = score
                
                decrypted_text = best_result if best_result else encrypted_payload
            else:
                # Unknown cipher type - try common methods
                decrypted_text = f"Unknown cipher: {cipher_type}"
            
            challenge_three_out = decrypted_text
        else:
            # Try AI analysis as fallback if we have some data but couldn't parse it properly
            if log_string and ENABLE_AI_FALLBACK:
                try:
                    prompt = f"""
You are a cryptanalysis expert. Analyze this log entry and decrypt any encrypted information.

LOG ENTRY: {log_string}

COMMON CIPHER TYPES:
- RAILFENCE: Rail fence cipher (usually 3 rails)
- KEYWORD: Keyword substitution cipher (often uses "SHADOW")
- POLYBIUS: Polybius square cipher (5x5 grid, I/J combined)
- ROTATION_CIPHER/CAESAR: Caesar cipher (try different shifts, especially ROT13)
- ATBASH: Atbash cipher (A=Z, B=Y, etc.)

INSTRUCTIONS:
1. Extract the cipher type and encrypted payload from the log
2. Apply the appropriate decryption method
3. Return the decrypted text

Respond with ONLY the decrypted text, no explanations.
"""
                    
                    data = {
                        "model": OPENAI_MODEL,
                        "messages": [
                            {"role": "system", "content": "You are a skilled cryptanalyst."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": OPENAI_TEMPERATURE
                    }
                    resp = requests.post(OPENAI_URL, headers=HEADERS, data=json.dumps(data))
                    if resp.status_code == 200:
                        content = resp.json()["choices"][0]["message"]["content"].strip()
                        challenge_three_out = content
                        logger.info("Challenge 3 AI fallback successful: %s", content)
                    else:
                        logger.error("Challenge 3 AI fallback failed: %s", resp.text)
                        challenge_three_out = "Could not decrypt log entry"
                except Exception as e:
                    logger.error("Challenge 3 AI fallback exception: %s", e)
                    challenge_three_out = "Could not decrypt log entry"
            else:
                challenge_three_out = "Could not parse cipher type or encrypted payload from log"
    else:
        challenge_three_out = "No challenge_three log string provided"

    # Challenge 4 - Final Communication Decryption
    challenge_four_out = None
    
    # Use the results from previous challenges to decrypt the final message
    if challenge_one_out and challenge_two_out and challenge_three_out:
        # Try to create a meaningful final decryption
        # Use Challenge 1 result as the base message to decrypt
        base_message = str(challenge_one_out)
        
        # Extract potential keys from all challenges
        potential_keys = []
        
        # From Challenge 1
        if challenge_one_out:
            potential_keys.append(str(challenge_one_out))
        
        # From Challenge 2
        if challenge_two_out:
            potential_keys.append(str(challenge_two_out))
            try:
                # If it's a number, also try as Caesar shift
                num_val = int(challenge_two_out)
                if 1 <= num_val <= 25:
                    potential_keys.append(f"SHIFT_{num_val}")
            except ValueError:
                pass
        
        # From Challenge 3
        if challenge_three_out:
            potential_keys.append(str(challenge_three_out))
        
        # Try various decryption methods
        best_result = base_message
        
        # Method 1: Try Caesar cipher with Challenge 2 as shift
        try:
            shift = int(challenge_two_out) if challenge_two_out.isdigit() else 13
            caesar_result = ""
            for char in base_message.upper():
                if char.isalpha():
                    caesar_result += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                else:
                    caesar_result += char
            
            # Check if result looks meaningful
            if any(word in caesar_result.upper() for word in config.MEANINGFUL_WORDS):
                best_result = caesar_result
        except:
            pass
        
        # Method 2: Try using Challenge 3 result as Vigenère key
        try:
            key = str(challenge_three_out).upper()
            if key and key.isalpha():
                vigenere_result = ""
                key_index = 0
                for char in base_message.upper():
                    if char.isalpha():
                        shift = ord(key[key_index % len(key)]) - ord('A')
                        vigenere_result += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                        key_index += 1
                    else:
                        vigenere_result += char
                
                if any(word in vigenere_result.upper() for word in config.MEANINGFUL_WORDS):
                    best_result = vigenere_result
        except:
            pass
        
        # Method 3: Simple reversal
        reverse_result = base_message[::-1]
        if any(word in reverse_result.upper() for word in config.MEANINGFUL_WORDS):
            best_result = reverse_result
        
        # Method 4: Atbash cipher
        try:
            atbash_result = ""
            for char in base_message.upper():
                if char.isalpha():
                    atbash_result += chr(ord('Z') - (ord(char) - ord('A')))
                else:
                    atbash_result += char
            
            if any(word in atbash_result.upper() for word in config.MEANINGFUL_WORDS):
                best_result = atbash_result
        except:
            pass
        
        challenge_four_out = best_result
    else:
        challenge_four_out = "Unable to combine previous challenge results"

    # Ensure all challenge outputs are strings as required by API
    challenge_one_str = str(challenge_one_out) if challenge_one_out is not None else "No result"
    challenge_two_str = str(challenge_two_out) if challenge_two_out is not None else "No result"
    challenge_three_str = str(challenge_three_out) if challenge_three_out is not None else "No result"
    challenge_four_str = str(challenge_four_out) if challenge_four_out is not None else "No result"
    
    # Prepare response
    response = {
        "challenge_one": challenge_one_str,
        "challenge_two": challenge_two_str,
        "challenge_three": challenge_three_str,
        "challenge_four": challenge_four_str
    }
    
    # Log the response for debugging
    logger.info("Operation Safeguard response: %s", response)
    
    return jsonify(response)


if __name__ == "__main__":
    # Only run the app if this file is executed directly
    app.run(debug=True, port=5000)
