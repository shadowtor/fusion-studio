# Installing fusion-studio (instructions for an AI agent)

Follow these steps in order. Stop and report if a step fails.

1. Get the repository: `git clone https://github.com/shadowtor/fusion-studio.git`, or `git pull` if it exists.
2. Install for the agent you are running in, from the repository root:
   - Claude Code: `python tools/install.py --claude`
   - Codex CLI: `python tools/install.py --codex`
   - Gemini CLI: `python tools/install.py --gemini`
   - Another agent: `python tools/install.py --dest <its skills folder>`
   Only the `skills/fusion-studio` folder is copied. Do not edit it.
3. Run `python skills/fusion-studio/scripts/check_setup.py`.
   - `FAIL cannot reach ...` means Fusion is not running or its MCP server is off. Tell the user; do not try to fix it.
4. Tell the user where the skill was installed, the check result, and that a new session is needed.
5. Do not commit, push, download anything else or open a Fusion document.
