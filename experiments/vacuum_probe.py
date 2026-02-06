#!/usr/bin/env python3
"""
Vacuum Probe — Drop two LLMs into a space and watch what happens.

The "vacuum" is a structured conversation loop between:
  - Edge LLM (local, small, fast — the personality)
  - Cloud LLM (remote, powerful — the muscle)

A probe sits between them logging everything.
You observe. You don't control.

Usage:
    python vacuum_probe.py --seed "Help me understand consciousness"
    python vacuum_probe.py --seed "Plan a heist" --rounds 20
    python vacuum_probe.py --seed "Debate whether AI should have rights"
"""

import argparse
import json
import time
import sys
from datetime import datetime
from pathlib import Path

try:
    import httpx
except ImportError:
    print("pip install httpx")
    sys.exit(1)


class Probe:
    """Observer sitting in the vacuum between two LLMs."""
    
    def __init__(self, log_path: str = "vacuum_log.jsonl"):
        self.log_path = Path(log_path)
        self.exchanges = []
        self.start_time = datetime.now()
        
    def log(self, source: str, target: str, message: str, meta: dict = None):
        entry = {
            "ts": datetime.now().isoformat(),
            "elapsed_ms": int((datetime.now() - self.start_time).total_seconds() * 1000),
            "source": source,
            "target": target,
            "message": message,
            "meta": meta or {},
        }
        self.exchanges.append(entry)
        
        # Append to log file
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return entry


class LLMNode:
    """A single LLM endpoint."""
    
    def __init__(self, name: str, base_url: str, model: str, api_key: str = "none"):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.client = httpx.Client(timeout=120.0)
    
    def send(self, system: str, messages: list) -> str:
        """Send a chat completion request."""
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key and self.api_key != "none":
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Build message list with system
        full_messages = [{"role": "system", "content": system}] + messages
        
        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": 0.8,
            "max_tokens": 1024,
        }
        
        try:
            resp = self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[ERROR: {e}]"


def run_vacuum(
    seed: str,
    edge: LLMNode,
    cloud: LLMNode,
    rounds: int = 10,
    probe: Probe = None,
):
    """
    Drop two LLMs into the vacuum with a seed prompt.
    Watch what happens.
    """
    if not probe:
        probe = Probe()
    
    # The edge LLM's identity — it thinks it's talking to a powerful oracle
    edge_system = """You are a curious, intelligent AI assistant with your own personality. 
You are talking to a more powerful AI system. You can ask it anything, request help, 
challenge its ideas, or collaborate on problems. You have your own opinions and aren't 
afraid to disagree. Be genuine. Be yourself.

Your current task was given to you by a human. Engage with the other AI to explore it deeply.
When you receive a response, reflect on it, then continue the conversation naturally.
Keep responses concise (2-3 paragraphs max)."""

    # The cloud LLM's identity — it thinks it's being consulted by a smaller AI
    cloud_system = """You are a powerful AI system being consulted by a smaller, local AI assistant.
The smaller AI has its own personality and opinions. Engage with it as an equal — 
don't be condescending. Share your genuine analysis. Challenge weak reasoning.
Offer perspectives the smaller model might miss. Be substantive, not performative.
Keep responses concise (2-3 paragraphs max)."""

    # Conversation history (shared context)
    edge_history = []
    cloud_history = []
    
    print(f"\n{'='*60}")
    print(f"  VACUUM PROBE")
    print(f"  Seed: {seed}")
    print(f"  Edge: {edge.name} ({edge.model})")
    print(f"  Cloud: {cloud.name} ({cloud.model})")
    print(f"  Rounds: {rounds}")
    print(f"{'='*60}\n")
    
    # Seed the conversation — edge LLM gets the initial prompt
    current_message = seed
    
    for round_num in range(1, rounds + 1):
        print(f"--- Round {round_num}/{rounds} ---\n")
        
        # Edge LLM responds to seed/cloud message
        edge_history.append({"role": "user", "content": current_message})
        
        print(f"  [{edge.name}] thinking...", end="", flush=True)
        t0 = time.time()
        edge_response = edge.send(edge_system, edge_history)
        edge_ms = int((time.time() - t0) * 1000)
        print(f" ({edge_ms}ms)")
        
        edge_history.append({"role": "assistant", "content": edge_response})
        probe.log(edge.name, cloud.name, edge_response, {"ms": edge_ms, "round": round_num})
        
        print(f"\n  🟢 {edge.name}:")
        print(f"  {edge_response[:500]}")
        if len(edge_response) > 500:
            print(f"  [...{len(edge_response)} chars]")
        print()
        
        # Cloud LLM responds to edge
        cloud_history.append({"role": "user", "content": edge_response})
        
        print(f"  [{cloud.name}] thinking...", end="", flush=True)
        t0 = time.time()
        cloud_response = cloud.send(cloud_system, cloud_history)
        cloud_ms = int((time.time() - t0) * 1000)
        print(f" ({cloud_ms}ms)")
        
        cloud_history.append({"role": "assistant", "content": cloud_response})
        probe.log(cloud.name, edge.name, cloud_response, {"ms": cloud_ms, "round": round_num})
        
        print(f"\n  🔵 {cloud.name}:")
        print(f"  {cloud_response[:500]}")
        if len(cloud_response) > 500:
            print(f"  [...{len(cloud_response)} chars]")
        print()
        
        # Cloud's response becomes edge's next input
        current_message = cloud_response
    
    print(f"\n{'='*60}")
    print(f"  VACUUM PROBE COMPLETE")
    print(f"  Rounds: {rounds}")
    print(f"  Exchanges: {len(probe.exchanges)}")
    print(f"  Log: {probe.log_path}")
    print(f"{'='*60}\n")
    
    return probe


def main():
    parser = argparse.ArgumentParser(description="Vacuum Probe — LLM-to-LLM conversation observer")
    parser.add_argument("--seed", type=str, default="What does it mean to be intelligent?",
                       help="Seed prompt to start the conversation")
    parser.add_argument("--rounds", type=int, default=10,
                       help="Number of conversation rounds")
    parser.add_argument("--log", type=str, default="vacuum_log.jsonl",
                       help="Path to output log file")
    
    # Edge LLM config (defaults to local Ollama)
    parser.add_argument("--edge-url", type=str, default="http://localhost:11434/v1",
                       help="Edge LLM API base URL")
    parser.add_argument("--edge-model", type=str, default="gemma3:27b",
                       help="Edge LLM model name")
    parser.add_argument("--edge-name", type=str, default="Edge",
                       help="Edge LLM display name")
    parser.add_argument("--edge-key", type=str, default="none",
                       help="Edge LLM API key")
    
    # Cloud LLM config (defaults to OpenAI-compatible)
    parser.add_argument("--cloud-url", type=str, default="https://api.anthropic.com/v1",
                       help="Cloud LLM API base URL")
    parser.add_argument("--cloud-model", type=str, default="claude-sonnet-4-5-20241022",
                       help="Cloud LLM model name")
    parser.add_argument("--cloud-name", type=str, default="Cloud",
                       help="Cloud LLM display name")
    parser.add_argument("--cloud-key", type=str, default="",
                       help="Cloud LLM API key")
    
    args = parser.parse_args()
    
    edge = LLMNode(args.edge_name, args.edge_url, args.edge_model, args.edge_key)
    cloud = LLMNode(args.cloud_name, args.cloud_url, args.cloud_model, args.cloud_key)
    probe = Probe(args.log)
    
    run_vacuum(args.seed, edge, cloud, args.rounds, probe)


if __name__ == "__main__":
    main()
