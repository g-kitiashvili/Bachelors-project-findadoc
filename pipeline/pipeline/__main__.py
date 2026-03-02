"""CLI entrypoint for the Find-a-Doc pipeline.

Usage:
    python -m pipeline run [--source SOURCE_NAME | --all]
    python -m pipeline scheduler
"""

from __future__ import annotations

import argparse
import sys
import time


def cmd_run(args: argparse.Namespace) -> int:
    """One-shot run: invokes the requested scrapers and exits."""
    print(f"[pipeline] one-shot run requested (source={args.source!r}, all={args.all})")
    # TODO: wire scrapers; currently a no-op CLI shim.
    return 0


def cmd_scheduler(args: argparse.Namespace) -> int:  # noqa: ARG001
    """Long-running scheduler: keeps the process alive and triggers periodic runs."""
    print("[pipeline] scheduler started")
    # TODO: real APScheduler loop. Block here so the container stays up.
    while True:
        time.sleep(3600)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pipeline", description="Find-a-Doc data pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="One-shot run; exits when done.")
    p_run.add_argument("--source", help="Run a single scraper by name.")
    p_run.add_argument("--all", action="store_true", help="Run every registered scraper.")
    p_run.set_defaults(func=cmd_run)

    p_sched = sub.add_parser("scheduler", help="Long-running scheduler loop.")
    p_sched.set_defaults(func=cmd_scheduler)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
