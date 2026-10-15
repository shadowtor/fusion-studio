#!/usr/bin/env python3
"""Install (or remove) the fusion-studio skill for Claude Code, Codex CLI, Gemini CLI or any folder.

  python tools/install.py                 # Claude Code + Codex, copy mode (default)
  python tools/install.py --claude        # only ~/.claude/skills/fusion-studio
  python tools/install.py --codex         # only ~/.codex/skills/fusion-studio
  python tools/install.py --gemini        # only ~/.gemini/skills/fusion-studio
  python tools/install.py --dest DIR      # DIR/fusion-studio
  python tools/install.py --project       # ./.claude/skills/fusion-studio in the current project
  python tools/install.py --link          # symlink instead of copy (may need admin on Windows)
  python tools/install.py --uninstall     # remove the chosen targets
  python tools/install.py --check         # run the setup check afterwards

Installing replaces an existing fusion-studio folder in the target. Nothing is downloaded and no packages are installed.
"""
import argparse, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "skills", "fusion-studio")
NAME = "fusion-studio"


def targets(a):
    home = os.path.expanduser("~")
    only = a.claude or a.codex or a.gemini or a.dest or a.project
    t = []
    if a.dest:
        t.append(os.path.join(os.path.abspath(a.dest), NAME))
    if a.project:
        t.append(os.path.join(os.getcwd(), ".claude", "skills", NAME))
    if a.claude or not only:
        t.append(os.path.join(home, ".claude", "skills", NAME))
    if a.codex or not only:
        t.append(os.path.join(home, ".codex", "skills", NAME))
    if a.gemini:
        t.append(os.path.join(home, ".gemini", "skills", NAME))
    return t


def remove(path):
    if os.path.islink(path):
        os.unlink(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for f in ("--claude", "--codex", "--gemini", "--project", "--link", "--uninstall", "--check"):
        ap.add_argument(f, action="store_true")
    ap.add_argument("--dest")
    a = ap.parse_args()
    if not os.path.exists(os.path.join(SRC, "SKILL.md")):
        sys.exit(f"error: {SRC} has no SKILL.md; run this from a full clone of the repository")
    for t in targets(a):
        if a.uninstall:
            remove(t)
            print("removed", t)
            continue
        os.makedirs(os.path.dirname(t), exist_ok=True)
        remove(t)
        if a.link:
            os.symlink(SRC, t, target_is_directory=True)
            print("linked ", t, "->", SRC)
        else:
            shutil.copytree(SRC, t, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            print("copied ", t)
    if a.uninstall:
        return
    if a.check:
        subprocess.call([sys.executable, os.path.join(SRC, "scripts", "check_setup.py")])
    else:
        print("\nNext: python skills/fusion-studio/scripts/check_setup.py   (checks Python and the Fusion MCP server)")
        print("Then start a new agent session and ask for a part to model.")


if __name__ == "__main__":
    main()
