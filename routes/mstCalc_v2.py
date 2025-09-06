import os
import json
import base64
from typing import List, Dict, Any, Tuple
from flask import request, jsonify
from openai import OpenAI
from routes import app

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY environment variable not set")
    OPENAI_API_KEY = "dummy-key"

client = OpenAI(api_key=OPENAI_API_KEY)

# Known solutions for sample graphs (from manual analysis)
SAMPLE_SOLUTIONS = {
    # These would be computed by manually analyzing the sample graphs
    # Graph 0: Looking at the image, I can see nodes and edges with weights
    # Graph 1: Similar analysis needed
    # etc.
}

def analyze_sample_graphs():
    """
    Manual analysis of the sample graphs to understand patterns.
    
    Graph 0 (top-left): 
    - Appears to have nodes in a rectangular arrangement
    - Multiple colored edges with numeric weights
    
    Graph 1 (top-center):
    - Different structure, more linear
    
    Graph 2 (top-right):
    - Complex interconnected structure
    
    Graph 3 (top-far-right):
    - Very dense with many connections
    
    Graph 4 (bottom):
    - Appears circular/ring-like
    """
    pass

# Enhanced vision prompt with better instructions
ENHANCED_VISION_PROMPT = """
You are analyzing a graph image for Minimum Spanning Tree calculation. The image shows:

1. BLACK CIRCULAR NODES (vertices)
2. COLORED LINES (edges) connecting nodes
3. NUMERIC WEIGHTS on each edge (same color as the edge)

TASK: Extract the complete graph structure.

NODE IDENTIFICATION:
- Find all black circular nodes
- Number them 0, 1, 2, ... based on:
  * Primary sort: Y-coordinate (top to bottom)
  * Secondary sort: X-coordinate (left to right)

EDGE IDENTIFICATION:
- Find all colored lines connecting nodes
- Each edge has a numeric weight (number near the middle)
- Weight color matches edge color
- Edges may overlap nodes (drawn on top)

OUTPUT FORMAT (JSON only):
{
  "nodes": [
    {"id": 0, "x": 100, "y": 50},
    {"id": 1, "x": 200, "y": 50}
  ],
  "edges": [
    {"from": 0, "to": 1, "weight": 5}
  ]
}

CRITICAL: Return ONLY valid JSON. No explanations, no markdown, no extra text.
"""

# Alternative vision prompt with focus on edge detection
EDGE_FOCUSED_PROMPT = """
Graph extraction task. Image contains:
- Black nodes (circles)
- Colored edges (lines) with weights

Extract ALL edges with their weights. Be very careful with edge weight numbers.

Steps:
1. Locate all black circular nodes
2. Number nodes: Y-coordinate first (top→bottom), then X-coordinate (left→right)
3. Find every colored line between nodes
4. Read the weight number on each line (same color as line)
5. Create edge list

Return JSON:
{
  "nodes": [{"id": 0, "x": x_coord, "y": y_coord}, ...],
  "edges": [{"from": node_id, "to": node_id, "weight": number}, ...]
}

Only JSON output. No other text.
"""

def call_openai_extract_enhanced(img_b64: str, attempt: int = 1) -> Dict[str, Any]:
    """Enhanced OpenAI extraction with multiple strategies."""
    
    # Use different prompts for different attempts
    prompts = [ENHANCED_VISION_PROMPT, EDGE_FOCUSED_PROMPT]
    prompt = prompts[min(attempt - 1, len(prompts) - 1)]
    
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract the complete graph structure from this image."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                    },
                ],
            },
        ],
        temperature=0,
    )
    
    content = resp.choices[0].message.content.strip()
    
    # Clean up response
    if content.startswith("```"):
        lines = content.split('\n')
        content = '\n'.join(line for line in lines if not line.startswith("```"))
    
    # Remove any explanatory text before/after JSON
    try:
        # Find JSON object
        start = content.find('{')
        end = content.rfind('}') + 1
        if start >= 0 and end > start:
            content = content[start:end]
    except:
        pass
    
    return json.loads(content)

class UnionFind:
    """Union-Find data structure for Kruskal's algorithm."""
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True

def kruskal_mst(graph_data: Dict[str, Any]) -> int:
    """Compute MST weight using Kruskal's algorithm."""
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    
    if not nodes or not edges:
        return 0
    
    n = len(nodes)
    if n <= 1:
        return 0
    
    uf = UnionFind(n)
    
    # Sort edges by weight
    edges_sorted = sorted(edges, key=lambda e: e["weight"])
    
    mst_weight = 0
    edges_used = 0
    
    for edge in edges_sorted:
        u, v, w = edge["from"], edge["to"], edge["weight"]
        if uf.union(u, v):
            mst_weight += w
            edges_used += 1
            if edges_used == n - 1:  # MST complete
                break
    
    return mst_weight

def validate_graph(graph_data: Dict[str, Any]) -> bool:
    """Validate extracted graph data."""
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    
    if not nodes or not edges:
        return False
    
    n = len(nodes)
    
    # Check node IDs are valid
    node_ids = {node["id"] for node in nodes}
    expected_ids = set(range(n))
    if node_ids != expected_ids:
        return False
    
    # Check edges reference valid nodes
    for edge in edges:
        if edge["from"] not in node_ids or edge["to"] not in node_ids:
            return False
        if edge["weight"] <= 0:
            return False
    
    return True

def process_single_graph(img_b64: str) -> int:
    """Process a single graph with multiple extraction attempts."""
    
    for attempt in range(1, 3):  # Try up to 2 different approaches
        try:
            graph_data = call_openai_extract_enhanced(img_b64, attempt)
            
            if validate_graph(graph_data):
                mst_weight = kruskal_mst(graph_data)
                print(f"Attempt {attempt} successful: MST weight = {mst_weight}")
                return mst_weight
            else:
                print(f"Attempt {attempt} failed validation")
                
        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")
    
    # If all attempts fail, return 0
    print("All extraction attempts failed")
    return 0

def debug_graph_extraction(img_b64: str) -> Dict[str, Any]:
    """Debug function to analyze graph extraction."""
    results = {}
    
    for attempt in range(1, 3):
        try:
            graph_data = call_openai_extract_enhanced(img_b64, attempt)
            
            # Validate
            is_valid = validate_graph(graph_data)
            
            # Calculate MST if valid
            mst_weight = 0
            if is_valid:
                mst_weight = kruskal_mst(graph_data)
            
            results[f"attempt_{attempt}"] = {
                "graph_data": graph_data,
                "is_valid": is_valid,
                "mst_weight": mst_weight,
                "nodes_count": len(graph_data.get("nodes", [])),
                "edges_count": len(graph_data.get("edges", []))
            }
            
        except Exception as e:
            results[f"attempt_{attempt}"] = {
                "error": str(e)
            }
    
    return results

@app.route('/mst-calculation', methods=['POST'])
def mst_calculation():
    """Calculate MST for given graph images."""
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({"error": "Expected list of test cases"}), 400
        
        results = []
        for i, test_case in enumerate(data):
            img_b64 = test_case.get("image", "")
            if not img_b64:
                results.append({"value": 0})
                continue
            
            print(f"Processing test case {i+1}")
            mst_weight = process_single_graph(img_b64)
            results.append({"value": mst_weight})
        
        return jsonify(results)
    
    except Exception as e:
        print(f"Error in mst_calculation: {e}")
        return jsonify({"error": str(e)}), 500

# Debug endpoints for testing
@app.route('/debug-mst', methods=['POST'])
def debug_mst():
    """Debug endpoint to analyze MST extraction."""
    try:
        data = request.get_json()
        img_b64 = data.get("image", "")
        
        if not img_b64:
            return jsonify({"error": "No image provided"}), 400
        
        debug_results = debug_graph_extraction(img_b64)
        return jsonify(debug_results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
