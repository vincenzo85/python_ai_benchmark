#!/usr/bin/env python3
import os
import sys
import json
import time
import argparse
import logging
import statistics
import csv
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests

# -------------------------------------------------------------------------
# PROMPT TEMPLATES
# -------------------------------------------------------------------------

# 1. LOGIC TEST: Logical Fallacy Identification
LOGIC_PROMPT = """Analyze the following argument and identify the logical fallacy present.
Explain your reasoning clearly.

ARGUMENT:
"My opponent suggests that lowering taxes will be a good idea -- this is coming from a woman who eats a pint of Ben and Jerry’s each night!"

RESPONSE FORMAT (JSON):
{{
  "fallacy_name": "Name of the fallacy",
  "reasoning": "Explanation of why this is a fallacy",
  "correct": "YES/NO (Internal self-check)"
}}
"""

# 2. MATH TEST: Conditional Probability
MATH_PROMPT = """Solve this probability problem. Show your work step-by-step.

PROBLEM:
In a factory, Machine A produces 60% of the items and Machine B produces 40%. 
2% of the items produced by Machine A are defective, while 5% of the items produced by Machine B are defective.
If a randomly selected item is defective, what is the probability that it was produced by Machine B?

RESPONSE FORMAT (JSON):
{{
  "final_answer": "The numerical probability (e.g., 0.45 or 45%)",
  "steps": "Summary of steps taken",
  "calculation_check": "Validation of the final number"
}}
"""

# 3. CODING TEST: Recursive Algorithm (Tree Traversal)
CODING_PROMPT = """Write a Python function to solve the following problem.

PROBLEM:
Given a binary tree, find the maximum path sum. The path may start and end at any node in the tree.
The path must contain at least one node and does not need to go through the root.

REQUIREMENTS:
- Use Python 3.
- Include a 'maxPathSum' function.
- Handle negative node values correctly.
- Provide 2-3 unit tests.

RESPONSE FORMAT (JSON):
{{
  "code": "The full Python code string",
  "complexity": "Time and Space complexity analysis",
  "explanation": "Brief explanation of the algorithm"
}}
"""

TEST_CASES = [
    {
        "id": "test_logic_ad_hominem",
        "category": "LOGIC",
        "prompt": LOGIC_PROMPT,
        "expected_keyword": "Ad Hominem"
    },
    {
        "id": "test_math_bayes_theorem",
        "category": "MATH",
        "prompt": MATH_PROMPT,
        "expected_keyword": "0.625"  # or 62.5%
    },
    {
        "id": "test_code_max_path_sum",
        "category": "CODING",
        "prompt": CODING_PROMPT,
        "expected_keyword": "maxPathSum"
    }
]

# -------------------------------------------------------------------------
# UTILITIES
# -------------------------------------------------------------------------

def get_all_models(ollama_url: str) -> List[str]:
    try:
        r = requests.get(f"{ollama_url.rstrip('/')}/api/tags", timeout=10)
        r.raise_for_status()
        return [m["name"] for m in r.json().get("models", [])]
    except Exception as e:
        logging.error(f"❌ Cannot get models: {e}")
        return []

def parse_json_response(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    t = text.strip()
    
    # Try direct parsing
    try:
        obj = json.loads(t)
        if isinstance(obj, dict): return obj
    except Exception:
        pass

    # Try extracting from code blocks
    t_clean = t.replace("``````", "").strip()
    match = re.search(r"\{[\s\S]*?\}", t_clean)
    if match:
        try:
            obj = json.loads(match.group(0))
            if isinstance(obj, dict): return obj
        except Exception:
            return None
    return None

def check_correctness(test_case: Dict, response_obj: Dict, raw_text: str) -> bool:
    """Basic heuristic to check correctness based on keywords in JSON or raw text."""
    expected = test_case["expected_keyword"].lower()
    
    # Check inside JSON values first
    if response_obj:
        for val in response_obj.values():
            if isinstance(val, str) and expected in val.lower():
                return True
            if isinstance(val, (int, float)) and expected in str(val):
                return True
                
    # Fallback: check raw text
    return expected in raw_text.lower()

def ollama_generate(ollama_url: str, model: str, prompt: str, timeout_s: int = 300) -> Dict[str, Any]:
    url = f"{ollama_url.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json", # Attempt to enforce JSON
        "options": {
            "temperature": 0.1, # Low temp for logic/math
            "num_predict": 1024, # Higher limit for coding/reasoning
        }
    }
    t0 = time.time()
    try:
        r = requests.post(url, json=payload, timeout=timeout_s)
        latency = time.time() - t0
        r.raise_for_status()
        j = r.json()
        return {"success": True, "latency": latency, "response": j.get("response", ""), "error": None}
    except Exception as e:
        return {"success": False, "latency": time.time() - t0, "response": None, "error": str(e)}

# -------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Complex Benchmark: Logic, Math, Code")
    parser.add_argument("--ollama", default="http://192.168.1.252:11434", help="Ollama server URL")
    parser.add_argument("--models", help="Comma-separated list of models")
    parser.add_argument("--limit", type=int, default=5, help="Limit number of models")
    parser.add_argument("--outdir", default="runs_complex", help="Output directory")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    # Setup directories
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(args.outdir, f"bench_complex_{ts}")
    os.makedirs(run_dir, exist_ok=True)
    
    responses_file_path = os.path.join(run_dir, "full_responses.txt")
    summary_csv_path = os.path.join(run_dir, "benchmark_summary.csv")

    # Select Models
    if args.models:
        models_to_test = [m.strip() for m in args.models.split(",") if m.strip()]
    else:
        all_models = get_all_models(args.ollama)
        if not all_models:
            logging.error("❌ No models found.")
            return
        models_to_test = all_models[:args.limit]

    logging.info(f"🚀 Starting Benchmark on {len(models_to_test)} models")
    logging.info(f"📂 Saving full responses to: {responses_file_path}")

    results_summary = []

    with open(responses_file_path, "w", encoding="utf-8") as resp_file:
        for model in models_to_test:
            logging.info(f"\nTesting Model: {model}")
            resp_file.write(f"\n{'='*80}\nMODEL: {model}\n{'='*80}\n")
            
            model_stats = {
                "model": model,
                "logic_pass": False,
                "math_pass": False,
                "code_pass": False,
                "avg_latency": 0.0,
                "latencies": []
            }

            for tc in TEST_CASES:
                logging.info(f"  👉 Running {tc['category']} Test...")
                
                res = ollama_generate(args.ollama, model, tc["prompt"])
                
                # Write to full response file
                resp_file.write(f"\n--- TEST: {tc['category']} ({tc['id']}) ---\n")
                if res["success"]:
                    resp_file.write(res["response"] + "\n")
                else:
                    resp_file.write(f"[ERROR] {res['error']}\n")
                resp_file.write("-" * 40 + "\n")

                # Analyze result
                passed = False
                if res["success"]:
                    parsed = parse_json_response(res["response"])
                    passed = check_correctness(tc, parsed, res["response"])
                    model_stats["latencies"].append(res["latency"])
                
                if tc["category"] == "LOGIC": model_stats["logic_pass"] = passed
                if tc["category"] == "MATH": model_stats["math_pass"] = passed
                if tc["category"] == "CODING": model_stats["code_pass"] = passed
                
                status_icon = "✅" if passed else "❌"
                logging.info(f"     {status_icon} Pass: {passed} | Latency: {res['latency']:.2f}s")

            # Calculate Average Latency
            if model_stats["latencies"]:
                model_stats["avg_latency"] = statistics.mean(model_stats["latencies"])
            
            results_summary.append(model_stats)

    # Save CSV Summary
    with open(summary_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Model", "Avg Latency", "Logic", "Math", "Coding", "Total Score (/3)"])
        for s in results_summary:
            total_score = sum([s["logic_pass"], s["math_pass"], s["code_pass"]])
            writer.writerow([
                s["model"],
                f"{s['avg_latency']:.2f}s",
                "PASS" if s["logic_pass"] else "FAIL",
                "PASS" if s["math_pass"] else "FAIL",
                "PASS" if s["code_pass"] else "FAIL",
                total_score
            ])

    logging.info(f"\n✅ Benchmark Complete. Results saved to {run_dir}")

if __name__ == "__main__":
    main()
