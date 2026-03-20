"""CLI entrypoint for the Find-a-Doc pipeline.

Usage:
    python -m pipeline run [--source SOURCE_NAME | --all]
    python -m pipeline scheduler
"""

from __future__ import annotations

import sys

from pipeline.cli import main


if __name__ == "__main__":
    sys.exit(main())
