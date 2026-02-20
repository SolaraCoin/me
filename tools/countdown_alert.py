#!/usr/bin/env python3
"""
External Countdown Alert Tool (no browser automation)

Monitors countdown values from an external source and emits alerts when the
remaining time drops below a threshold.

Supported sources:
- stdin (interactive manual entry)
- file  (poll a text file produced by any external process/OCR tool)
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path


def parse_time(raw: str) -> int:
    raw = raw.strip()
    if not raw:
        raise ValueError("Empty input")

    if ":" in raw:
        parts = raw.split(":")
        if len(parts) != 2:
            raise ValueError("Time must be MM:SS")
        m = int(parts[0])
        s = int(parts[1])
        if m < 0 or s < 0 or s >= 60:
            raise ValueError("Invalid MM:SS value")
        return m * 60 + s

    value = float(raw)
    if value < 0:
        raise ValueError("Seconds cannot be negative")
    return int(value)


def alert(message: str, bells: int = 2) -> None:
    print(f"\n[ALERT] {message}")
    for _ in range(max(0, bells)):
        print("\a", end="", flush=True)
        time.sleep(0.12)
    print()


def evaluate(seconds: int, threshold: int, once: bool) -> bool:
    print(f"[INFO] Remaining: {seconds}s")
    if seconds < threshold:
        alert(f"Remaining time {seconds}s is below threshold {threshold}s")
        return once
    return False


def run_stdin(threshold: int, once: bool, poll_ms: int) -> None:
    print("Source: stdin")
    print("Enter remaining time as MM:SS or seconds (e.g. 00:53 or 53)")
    print(f"Alert threshold: < {threshold}s | Ctrl+C to exit\n")

    while True:
        try:
            raw = input("Remaining time> ")
            seconds = parse_time(raw)
        except ValueError as exc:
            print(f"[WARN] {exc}")
            continue
        except KeyboardInterrupt:
            print("\nStopped.")
            return

        if evaluate(seconds, threshold, once):
            return
        time.sleep(max(0, poll_ms) / 1000)


def run_file(threshold: int, once: bool, poll_ms: int, path: Path) -> None:
    print("Source: file")
    print(f"Watching: {path}")
    print(f"Alert threshold: < {threshold}s | Ctrl+C to exit\n")

    last_content: str | None = None

    while True:
        try:
            if not path.exists():
                time.sleep(max(50, poll_ms) / 1000)
                continue

            content = path.read_text(encoding="utf-8").strip()
            if not content or content == last_content:
                time.sleep(max(50, poll_ms) / 1000)
                continue

            last_content = content
            seconds = parse_time(content)
            if evaluate(seconds, threshold, once):
                return

            time.sleep(max(0, poll_ms) / 1000)
        except ValueError as exc:
            print(f"[WARN] Invalid file content '{last_content}': {exc}")
            time.sleep(max(50, poll_ms) / 1000)
        except KeyboardInterrupt:
            print("\nStopped.")
            return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="External countdown monitor that alerts below a threshold."
    )
    parser.add_argument("--threshold", type=int, default=54, help="Alert when remaining seconds are below this value (default: 54)")
    parser.add_argument("--once", action="store_true", help="Exit after first alert")
    parser.add_argument("--poll-ms", type=int, default=250, help="Polling interval in milliseconds (default: 250)")
    parser.add_argument("--source", choices=["stdin", "file"], default="stdin", help="Input source (default: stdin)")
    parser.add_argument("--file", default="/tmp/countdown.txt", help="File path when --source file (default: /tmp/countdown.txt)")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.threshold < 0:
        raise SystemExit("--threshold must be >= 0")
    if args.poll_ms < 0:
        raise SystemExit("--poll-ms must be >= 0")

    if args.source == "stdin":
        run_stdin(threshold=args.threshold, once=args.once, poll_ms=args.poll_ms)
    else:
        run_file(
            threshold=args.threshold,
            once=args.once,
            poll_ms=args.poll_ms,
            path=Path(args.file),
        )


if __name__ == "__main__":
    main()
