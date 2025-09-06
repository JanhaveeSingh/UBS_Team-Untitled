import os
import json
import base64
from typing import List, Dict, Any
from flask import request, jsonify
from openai import OpenAI
from routes import app

# Keep the original as backup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY environment variable not set")
    OPENAI_API_KEY = "dummy-key"

client = OpenAI(api_key=OPENAI_API_KEY)

# Original vision prompt and functions...
VISION_SYS_PROMPT = """
You are a graph analysis expert. Given an image of an undirected, weighted graph:

1. IDENTIFY NODES: Count black circular nodes and assign coordinates
2. IDENTIFY EDGES: Find colored lines connecting nodes with weights
3. EXTRACT WEIGHTS: Read the numbers on each edge (same color as edge)

CRITICAL NODE NUMBERING:
- Sort nodes by Y-coordinate first (top to bottom)
- Then by X-coordinate (left to right) 
- Number starting from 0

Return ONLY a JSON object:
{
  "nodes": [
    {"id": 0, "x": 100, "y": 50},
    {"id": 1, "x": 200, "y": 50}
  ],
  "edges": [
    {"from": 0, "to": 1, "weight": 5}
  ]
}

IMPORTANT: 
- Nodes are black circles
- Edges are colored lines with numbers
- Edge weights are the numbers shown on the lines
- Return only valid JSON, no other text
"""

def call_openai_extract(img_b64: str) -> Dict[str, Any]:
    """Call OpenAI vision to get nodes + edges JSON."""
    resp = client.chat.completions.create(
        model="gpt-4o",  # Using full gpt-4o for better accuracy
        messages=[
            {
                "role": "system",
                "content": VISION_SYS_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract the graph and return ONLY the JSON object. Pay special attention to node numbering - sort by Y first, then X."},
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
    
    # Clean up any markdown formatting
    if content.startswith("```"):
        lines = content.split('\n')
        content = '\n'.join(lines[1:-1])
    
    return json.loads(content)

class UnionFind:
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
            if edges_used == n - 1:
                break
    
    return mst_weight

def debug_kruskal_mst(img_b64: str) -> Dict[str, Any]:
    """Debug version that shows all steps."""
    try:
        # Extract graph
        graph_data = call_openai_extract(img_b64)
        print(f"Extracted graph: {graph_data}")
        
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        
        print(f"Nodes: {len(nodes)}")
        print(f"Edges: {len(edges)}")
        
        if not nodes or not edges:
            return {"error": "No nodes or edges found", "mst_weight": 0}
        
        n = len(nodes)
        uf = UnionFind(n)
        
        # Sort edges by weight
        edges_sorted = sorted(edges, key=lambda e: e["weight"])
        print(f"Sorted edges: {edges_sorted}")
        
        mst_weight = 0
        edges_used = 0
        mst_edges = []
        
        for edge in edges_sorted:
            u, v, w = edge["from"], edge["to"], edge["weight"]
            if uf.union(u, v):
                mst_weight += w
                edges_used += 1
                mst_edges.append(edge)
                print(f"Added edge {u}-{v} weight {w}, total: {mst_weight}")
                if edges_used == n - 1:
                    break
        
        return {
            "graph_data": graph_data,
            "mst_weight": mst_weight,
            "mst_edges": mst_edges,
            "edges_used": edges_used,
            "total_nodes": n
        }
        
    except Exception as e:
        return {"error": str(e), "mst_weight": 0}

@app.route('/mst-calculation', methods=['POST'])
def mst_calculation():
    """Calculate MST for given graph images."""
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({"error": "Expected list of test cases"}), 400
        
        results = []
        for test_case in data:
            img_b64 = test_case.get("image", "")
            if not img_b64:
                results.append({"value": 0})
                continue
            
            try:
                graph_data = call_openai_extract(img_b64)
                mst_weight = kruskal_mst(graph_data)
                results.append({"value": mst_weight})
            except Exception as e:
                print(f"Error processing test case: {e}")
                results.append({"value": 0})
        
        return jsonify(results)
    
    except Exception as e:
        print(f"Error in mst_calculation: {e}")
        return jsonify({"error": str(e)}), 500
