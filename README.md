# 🐍 slither-cli

A colorful terminal **Snake** game with a beautiful banner and locally-saved high scores.
No account. No servers. No config. Just `slither-cli` and play.

```
███████╗██╗     ██╗████████╗██╗  ██╗███████╗██████╗
██╔════╝██║     ██║╚══██╔══╝██║  ██║██╔════╝██╔══██╗
███████╗██║     ██║   ██║   ███████║█████╗  ██████╔╝
╚════██║██║     ██║   ██║   ██╔══██║██╔══╝  ██╔══██╗
███████║███████╗██║   ██║   ██║  ██║███████╗██║  ██║
╚══════╝╚══════╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
```

## Features

- 🌈 Colorful curses UI with a rainbow ASCII banner
- 🏆 Local high-score tracking (no accounts, no network)
- ⚡ Speed ramps up as your score grows
- ⌨️ Arrow keys **or** WASD, pause, restart
- 📦 Zero dependencies — pure Python standard library

## Install

### Homebrew

```sh
brew tap DibyoD/tap
brew install slither-cli
```

### From source

```sh
git clone https://github.com/DibyoD/slither-cli
cd slither-cli
pip install .
slither-cli
```

Or run it without installing:

```sh
python3 -m slither_cli
```

## How to play

| Key | Action |
| --- | --- |
| `← ↑ ↓ →` / `W A S D` | Move the snake |
| `P` | Pause / resume |
| `R` | Play again (on the game-over screen) |
| `M` | Back to the menu |
| `Q` | Quit |

Eat the ◆ to grow. Don't hit the walls or yourself. Beat your high score.

## Where are high scores stored?

In a small JSON file under your data directory:

- `$XDG_DATA_HOME/slither-cli/highscore.json`, or
- `~/.local/share/slither-cli/highscore.json` by default.

Delete that file to reset your stats.

## License

MIT — see [LICENSE](LICENSE).
