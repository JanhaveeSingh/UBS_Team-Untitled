import os
import json
import logging
from typing import List, Tuple, Dict, Any
from flask import request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

from routes import app


load_dotenv()

# --- Config / logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mst-openai")


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


# --- Kruskal MST ---
def kruskal_mst(num_nodes: int, edges: List[Tuple[int, int, int]]) -> int:
    if num_nodes <= 1:
        return 0
    
    parent = list(range(num_nodes))
    rank = [0] * num_nodes

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> bool:
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1
        return True

    # Sort edges by weight
    sorted_edges = sorted(edges, key=lambda e: e[2])
    
    total_weight = 0
    edges_used = 0
    
    for u, v, w in sorted_edges:
        # Validate node indices
        if not (0 <= u < num_nodes and 0 <= v < num_nodes):
            continue
            
        # Try to add this edge to MST
        if union(u, v):
            total_weight += w
            edges_used += 1
            # MST is complete when we have n-1 edges
            if edges_used == num_nodes - 1:
                break
    
    # If we couldn't form a complete MST, return 0
    if edges_used != num_nodes - 1:
        logger.warning(f"MST incomplete: used {edges_used} edges, need {num_nodes - 1}")
        return 0
        
    return total_weight

def test_mst_algorithm():
    """Test the MST algorithm with known examples."""
    # Test case 1: Simple triangle
    edges1 = [(0, 1, 3), (1, 2, 4), (0, 2, 5)]
    result1 = kruskal_mst(3, edges1)
    logger.info(f"Test 1: Triangle graph MST = {result1} (expected 7)")
    
    # Test case 2: Square with diagonal
    edges2 = [(0, 1, 1), (1, 2, 2), (2, 3, 3), (0, 3, 4), (0, 2, 5)]
    result2 = kruskal_mst(4, edges2)
    logger.info(f"Test 2: Square graph MST = {result2} (expected 6)")

# --- Vision system prompt ---
VISION_SYS_PROMPT = (
    "You are an expert visual graph reader. The image shows an undirected, connected, weighted graph. "
    "Black filled circles are nodes. Colored lines are edges. Near the midpoint of each edge there is an integer weight "
    "drawn (same color as the edge).\n\n"
    "IMPORTANT: Assign node IDs deterministically as follows: find black circle centers and sort by (y, then x), ascending "
    "(top-to-bottom then left-to-right). Number them 0,1,2,... in that order.\n\n"
    "For each edge, identify the two nodes it connects and the weight value. Make sure to:\n"
    "1. Count all black circles to get the total number of nodes\n"
    "2. For each edge, determine which two nodes it connects\n"
    "3. Read the weight value near the middle of each edge\n"
    "4. Ensure all nodes are numbered 0 to (total_nodes-1)\n\n"
    "Return STRICT JSON ONLY with this exact schema:\n"
    "{\n"
    '  "nodes": <int>,\n'
    '  "edges": [{"u": <int>, "v": <int>, "w": <int>}, ...]\n'
    "}\n"
    "No markdown fences, no prose, no explanations. Weights are positive integers. Edges are undirected (list each once)."
)

def call_openai_extract(img_b64: str) -> Dict[str, Any]:
    """Call OpenAI vision to get nodes + edges JSON."""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",  # Using gpt-4o-mini for cheaper/faster runs
        messages=[
            {
                "role": "system",
                "content": VISION_SYS_PROMPT,
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract the graph and return ONLY the JSON object."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                    },
                ],
            },
        ],
        temperature=0,
    )
    text = resp.choices[0].message.content.strip()

    # Handle possible code fences
    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]

    # Extract JSON
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Model did not return JSON: {text[:200]}...")
    data = json.loads(text[start:end+1])

    if "nodes" not in data or "edges" not in data:
        raise ValueError("Missing 'nodes' or 'edges' in model output.")

    edges = [(int(e["u"]), int(e["v"]), int(e["w"])) for e in data["edges"]]
    return {"nodes": int(data["nodes"]), "edges": edges}

@app.route("/mst-calculation", methods=["POST"])
def mst_calculation():
    """
    Input JSON: [{"image": "<base64 png>"}, {"image": "<base64 png>"}]
    Output JSON: [{"value": int}, {"value": int}]
    """
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is not set")
        return jsonify({"error": "OPENAI_API_KEY is not set"}), 500

    try:
        cases = request.get_json(force=True)
        if not isinstance(cases, list):
            logger.error("Invalid input: expected list of cases")
            return jsonify({"error": "Invalid input format"}), 400
            
        logger.info(f"Processing {len(cases)} test cases")
        results = []

        for idx, case in enumerate(cases):
            logger.info(f"Processing case {idx}")
            
            if not isinstance(case, dict):
                logger.warning(f"Case {idx}: invalid case format")
                results.append({"value": 0})
                continue
                
            img_b64 = case.get("image", "")
            if not img_b64 or not isinstance(img_b64, str):
                logger.warning(f"Case {idx}: missing or invalid image")
                results.append({"value": 0})
                continue

            logger.info(f"Case {idx}: received base64 image (length={len(img_b64)})")

            try:
                parsed = call_openai_extract(img_b64)
                num_nodes = parsed["nodes"]
                edges = parsed["edges"]
                
                logger.info(f"Case {idx}: extracted {num_nodes} nodes, {len(edges)} edges")
                if len(edges) > 0:
                    logger.info(f"Case {idx}: sample edges = {edges[:3]}{'...' if len(edges) > 3 else ''}")
                
                if num_nodes <= 0:
                    logger.warning(f"Case {idx}: invalid node count {num_nodes}")
                    results.append({"value": 0})
                    continue
                
                # Validate that we have enough edges for connectivity
                if len(edges) < num_nodes - 1:
                    logger.warning(f"Case {idx}: insufficient edges ({len(edges)}) for {num_nodes} nodes")
                    
                value = kruskal_mst(num_nodes, edges)
                logger.info(f"Case {idx}: MST weight = {value}")
                
            except Exception as e:
                logger.error(f"Case {idx}: processing failed: {e}")
                logger.error(f"Case {idx}: error type: {type(e).__name__}")
                value = 0

            results.append({"value": int(value)})

        logger.info(f"Final results: {results}")
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/mst-test", methods=["GET"])
def mst_test():
    """Test endpoint to verify MST algorithm works correctly."""
    try:
        test_mst_algorithm()
        return jsonify({"status": "MST algorithm test completed", "check_logs": True})
    except Exception as e:
        logger.error(f"MST test failed: {e}")
        return jsonify({"error": str(e)}), 500



