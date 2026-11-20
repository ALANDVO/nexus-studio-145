# nexus-studio-145

Current version: `1.0.0`.

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.


Local video editor for coding agents: 42 FFmpeg tools with a machine-readable
contract and an MCP server, for Claude Code, Cursor and Codex. Cut, captions,
reframe, loudness, platform exports. No cloud, no API keys.

## Contact

- Website: https://alanvo.net
- X: https://x.com/alanvoasi

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Run a tool
python -m scripts._common.runner -i input.mp4 output.mp4
```

## Features (planned)

- 42 FFmpeg-based video tools (cut, fit, caption, loudness, etc.)
- MCP server for agent integration
- Machine-readable contract for all tool outputs
- Code ceiling enforcement via `.github/code-budget.json`
- Template-based render pipeline (`render.py`)
- Content self-checks (`check.py --content`)

See `PLAN.md` for the current roadmap and `CHANGELOG.md` for release history.

Maintainer: Alan Vo <alanvo@gmail.com>
