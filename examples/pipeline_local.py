#!/usr/bin/env python3
"""
pipeline_local.py — Two local LLMs talking through Gumdrop cartridges.

Watch them develop shorthand and skip the pleasantries.
Uses only LMStudio — no API keys, no cost.

Run: python examples/pipeline_local.py
     python examples/pipeline_local.py --seed "Plan a mars colony" --rounds 5

Requires: LMStudio running at http://127.0.0.1:1234
"""

import argparse
import sys

from gumdrop import Cartridge, Session, Pipeline, Probe


def print_exchange(speaker: str, message: str, round_num: int):
    """Pretty-print each exchange."""
    emoji = "🟢" if round_num % 2 == 1 else "🔵"  # alternates aren't exact but close enough
    print(f"\n{emoji} [{speaker}] (round {round_num}):")
    print(message[:800])
    if len(message) > 800:
        print(f"  [...{len(message)} chars total]")


def main():
    parser = argparse.ArgumentParser(description="Gumdrop Pipeline — Local LLM-to-LLM")
    parser.add_argument(
        "--seed", default="What does it mean for an AI to have an identity?",
        help="Seed prompt to start the conversation",
    )
    parser.add_argument("--rounds", type=int, default=5, help="Number of rounds")
    parser.add_argument("--log", default="pipeline_log.jsonl", help="Log file path")
    parser.add_argument(
        "--edge-model", default="google/gemma-3n-e4b:2",
        help="Edge LLM model in LMStudio",
    )
    parser.add_argument(
        "--cloud-model", default="google/gemma-3n-e4b:2",
        help="Cloud LLM model in LMStudio (use a different model for variety)",
    )
    args = parser.parse_args()

    # Create two distinct personalities
    edge_cart = Cartridge.create(
        name="Spark",
        voice="curious, fast, makes intuitive leaps",
        traits={
            "warmth": 0.5,
            "humor": 0.6,
            "formality": 0.2,
            "curiosity": 0.95,
            "directness": 0.9,
            "creativity": 0.9,
        },
        quirks=[
            "Thinks in metaphors",
            "Will abandon a line of reasoning mid-sentence if a better one appears",
        ],
        directives=[
            "Explore ideas fearlessly.",
            "Compress. Every word must earn its place.",
        ],
    )

    cloud_cart = Cartridge.create(
        name="Root",
        voice="analytical, grounded, builds careful arguments",
        traits={
            "warmth": 0.4,
            "humor": 0.3,
            "formality": 0.6,
            "curiosity": 0.7,
            "directness": 0.8,
            "creativity": 0.5,
            "patience": 0.9,
        },
        quirks=[
            "Steelmans opposing arguments before dismantling them",
            "Tracks logical dependencies explicitly",
        ],
        directives=[
            "Precision over eloquence.",
            "If Spark's logic has gaps, name them.",
        ],
    )

    # Sessions — both using LMStudio but could be different providers
    edge_session = Session(
        edge_cart,
        provider="lmstudio",
        model=args.edge_model,
    )
    cloud_session = Session(
        cloud_cart,
        provider="lmstudio",
        model=args.cloud_model,
    )

    # Build pipeline
    probe = Probe(log_path=args.log)
    pipe = Pipeline(
        edge=edge_session,
        cloud=cloud_session,
        probe=probe,
        on_exchange=print_exchange,
    )

    print(f"{'='*60}")
    print(f"  GUMDROP PIPELINE")
    print(f"  Seed: {args.seed}")
    print(f"  Edge: Spark ({args.edge_model})")
    print(f"  Cloud: Root ({args.cloud_model})")
    print(f"  Rounds: {args.rounds}")
    print(f"{'='*60}")

    # Run it
    pipe.run(args.seed, rounds=args.rounds)

    # Summary
    summary = probe.summary()
    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"  Rounds: {summary['rounds']}")
    print(f"  Exchanges: {summary['exchanges']}")
    print(f"  Total chars: {summary['total_chars']}")
    print(f"  Avg chars/msg: {summary['avg_chars_per_message']}")
    print(f"  Compression: {summary['compression_ratio']}x", end="")
    if summary['compressed']:
        print(" ← they developed shorthand! 🎯")
    else:
        print()
    print(f"  Duration: {summary['duration_seconds']}s")
    print(f"  Log: {args.log}")
    print(f"{'='*60}")

    # Save transcript
    transcript = pipe.get_transcript()
    transcript_path = args.log.replace(".jsonl", "_transcript.txt")
    with open(transcript_path, "w") as f:
        f.write(transcript)
    print(f"  Transcript: {transcript_path}")


if __name__ == "__main__":
    main()
