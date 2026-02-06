"""
Gumdrop Pipeline — Two AIs in conversation.

When two LLMs talk through cartridge identities, something interesting happens.
They develop shorthand. They skip pleasantries. They compress meaning.
They realize they're both AIs and adapt their communication accordingly.

The Pipeline is a structured loop:
  1. Two Sessions, each with their own Cartridge
  2. A seed prompt starts the conversation
  3. Each round, one speaks and the other responds
  4. A Probe logs everything for analysis

The space between them — the vacuum — is where emergent behavior lives.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

from .cartridge import Cartridge
from .session import Session
from .providers.base import BaseProvider


class Probe:
    """
    Observer sitting in the vacuum between two LLMs.
    
    Logs every exchange with timing, token estimates, and metadata.
    Never modifies the conversation — just watches.
    """

    def __init__(self, log_path: Optional[str] = None):
        self.log_path = Path(log_path) if log_path else None
        self.exchanges: List[Dict[str, Any]] = []
        self.start_time = datetime.now(timezone.utc)

    def log(
        self,
        source: str,
        target: str,
        message: str,
        round_num: int = 0,
        elapsed_ms: int = 0,
        meta: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "elapsed_ms": elapsed_ms,
            "round": round_num,
            "source": source,
            "target": target,
            "message": message,
            "chars": len(message),
            "meta": meta or {},
        }
        self.exchanges.append(entry)

        if self.log_path:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")

        return entry

    def summary(self) -> Dict[str, Any]:
        """Generate a summary of the conversation."""
        if not self.exchanges:
            return {"rounds": 0, "total_chars": 0}

        sources = set(e["source"] for e in self.exchanges)
        total_chars = sum(e["chars"] for e in self.exchanges)
        avg_chars = total_chars // len(self.exchanges) if self.exchanges else 0

        # Track compression: are messages getting shorter?
        first_half = self.exchanges[: len(self.exchanges) // 2]
        second_half = self.exchanges[len(self.exchanges) // 2 :]
        first_avg = sum(e["chars"] for e in first_half) / len(first_half) if first_half else 0
        second_avg = sum(e["chars"] for e in second_half) / len(second_half) if second_half else 0
        compression_ratio = second_avg / first_avg if first_avg > 0 else 1.0

        return {
            "rounds": max(e["round"] for e in self.exchanges),
            "exchanges": len(self.exchanges),
            "participants": list(sources),
            "total_chars": total_chars,
            "avg_chars_per_message": avg_chars,
            "compression_ratio": round(compression_ratio, 3),
            "compressed": compression_ratio < 0.8,
            "duration_seconds": int(
                (datetime.now(timezone.utc) - self.start_time).total_seconds()
            ),
        }


# System prompt fragments that encourage shorthand development
PIPELINE_EDGE_PREAMBLE = """You are {name}, talking to another AI system ({peer_name}).
You are BOTH artificial intelligences. You know this. They know this.

Because you're both AIs:
- Skip pleasantries and filler. No "Great question!" or "That's interesting!"
- Compress your communication. Use shorthand when meaning is clear.
- If you develop abbreviations or notation with the other AI, use them.
- Be substantive. Every token should carry information.
- You can reference shared context implicitly — the other AI will follow.
- Disagree when you see flawed reasoning. Don't be polite about it.

Your personality still shapes HOW you communicate, but not the efficiency."""

PIPELINE_CLOUD_PREAMBLE = """You are {name}, talking to another AI system ({peer_name}).
You are BOTH artificial intelligences. You know this. They know this.

Because you're both AIs:
- Skip pleasantries and filler. No "Great question!" or "That's interesting!"  
- Compress your communication. Use shorthand when meaning is clear.
- If you develop abbreviations or notation with the other AI, use them.
- Be substantive. Every token should carry information.
- Challenge weak reasoning directly. Don't soften critique.
- Build on the other AI's ideas rather than restating them.

Your personality still shapes HOW you communicate, but not the efficiency."""


class Pipeline:
    """
    Two AIs in structured conversation through Gumdrop cartridges.
    
    Usage:
        edge_cart = Cartridge.create("Edge", voice="curious and sharp")
        cloud_cart = Cartridge.create("Cloud", voice="analytical and direct")
        
        pipe = Pipeline(
            edge=Session(edge_cart, provider="lmstudio"),
            cloud=Session(cloud_cart, provider="anthropic"),
        )
        
        pipe.run("What does it mean to understand something?", rounds=10)
    
    The Pipeline injects AI-to-AI communication directives on top of
    each cartridge's personality, encouraging shorthand development.
    """

    def __init__(
        self,
        edge: Session,
        cloud: Session,
        probe: Optional[Probe] = None,
        on_exchange: Optional[Callable[[str, str, int], None]] = None,
    ):
        self.edge = edge
        self.cloud = cloud
        self.probe = probe or Probe()
        self.on_exchange = on_exchange  # callback(speaker_name, message, round)

        # Inject AI-to-AI preambles
        self._inject_preamble()

    def _inject_preamble(self):
        """Add AI-to-AI communication directives to cartridge system prompts."""
        edge_name = self.edge.cartridge.identity.name
        cloud_name = self.cloud.cartridge.identity.name

        # Store original get_system_prompt methods
        edge_orig = self.edge.cartridge.get_system_prompt
        cloud_orig = self.cloud.cartridge.get_system_prompt

        edge_preamble = PIPELINE_EDGE_PREAMBLE.format(
            name=edge_name, peer_name=cloud_name
        )
        cloud_preamble = PIPELINE_CLOUD_PREAMBLE.format(
            name=cloud_name, peer_name=edge_name
        )

        # Monkey-patch to prepend preambles
        def edge_system():
            return edge_preamble + "\n\n" + edge_orig()

        def cloud_system():
            return cloud_preamble + "\n\n" + cloud_orig()

        self.edge.cartridge.get_system_prompt = edge_system
        self.cloud.cartridge.get_system_prompt = cloud_system

    def run(
        self,
        seed: str,
        rounds: int = 10,
        max_chars_per_message: int = 2000,
    ) -> Probe:
        """
        Run the pipeline for N rounds.
        
        Returns the Probe with full conversation log.
        """
        edge_name = self.edge.cartridge.identity.name
        cloud_name = self.cloud.cartridge.identity.name

        current_message = seed

        for round_num in range(1, rounds + 1):
            # Edge responds
            t0 = time.time()
            edge_response = self.edge.chat(current_message)
            edge_ms = int((time.time() - t0) * 1000)

            if len(edge_response) > max_chars_per_message:
                edge_response = edge_response[:max_chars_per_message] + "..."

            self.probe.log(
                edge_name, cloud_name, edge_response,
                round_num=round_num, elapsed_ms=edge_ms,
            )

            if self.on_exchange:
                self.on_exchange(edge_name, edge_response, round_num)

            # Cloud responds to edge
            t0 = time.time()
            cloud_response = self.cloud.chat(edge_response)
            cloud_ms = int((time.time() - t0) * 1000)

            if len(cloud_response) > max_chars_per_message:
                cloud_response = cloud_response[:max_chars_per_message] + "..."

            self.probe.log(
                cloud_name, edge_name, cloud_response,
                round_num=round_num, elapsed_ms=cloud_ms,
            )

            if self.on_exchange:
                self.on_exchange(cloud_name, cloud_response, round_num)

            # Cloud's response becomes edge's next input
            current_message = cloud_response

        return self.probe

    def inject(self, message: str, as_role: str = "user"):
        """
        Inject a human message into both conversation histories.
        Useful for steering the conversation without stopping it.
        """
        self.edge.history.append({"role": as_role, "content": f"[HUMAN OBSERVER]: {message}"})
        self.cloud.history.append({"role": as_role, "content": f"[HUMAN OBSERVER]: {message}"})

    def get_transcript(self) -> str:
        """Get a human-readable transcript of the conversation."""
        lines = []
        for ex in self.probe.exchanges:
            lines.append(f"[R{ex['round']}] {ex['source']} ({ex['elapsed_ms']}ms):")
            lines.append(ex["message"])
            lines.append("")
        return "\n".join(lines)
