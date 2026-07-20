"""Entry point for `slither-cli`."""

from __future__ import annotations

import curses
import sys

from . import __version__
from .game import run


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in ("-v", "--version"):
        print(f"slither-cli {__version__}")
        return 0
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(
            "slither-cli — a colorful terminal Snake game\n\n"
            "Usage: slither-cli\n\n"
            "In-game controls:\n"
            "  Arrow keys / W A S D   move\n"
            "  P                      pause\n"
            "  Q                      quit\n"
            "  R                      play again (on game-over screen)\n\n"
            "High scores are saved locally under ~/.local/share/slither-cli.\n"
        )
        return 0

    try:
        curses.wrapper(run)
    except KeyboardInterrupt:
        pass
    except curses.error as exc:
        print(f"slither-cli: terminal error: {exc}", file=sys.stderr)
        print("Try enlarging your terminal window.", file=sys.stderr)
        return 1
    print("Thanks for playing slither-cli! 🐍")
    return 0


if __name__ == "__main__":
    sys.exit(main())
