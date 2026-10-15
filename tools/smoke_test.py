#!/usr/bin/env python3
"""Smoke test. Runs anywhere (CI included); the live-Fusion step runs only when the MCP server answers.

  python tools/smoke_test.py
"""
import json, os, py_compile, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skills", "fusion-studio")
S = os.path.join(SK, "scripts")


def ok(msg):
    print("OK  ", msg)


def fail(msg):
    print("FAIL", msg)
    sys.exit(1)


# 1. SKILL.md frontmatter and referenced files
text = open(os.path.join(SK, "SKILL.md"), encoding="utf-8").read()
m = re.match(r"---\nname: (\S+)\ndescription: (.+)\n---\n", text)
if not m or m.group(1) != "fusion-studio":
    fail("SKILL.md frontmatter")
ok("SKILL.md frontmatter")
for ref in re.findall(r"\]\((references/[^)]+)\)", text):
    if not os.path.exists(os.path.join(SK, ref)):
        fail("missing " + ref)
ok("SKILL.md links resolve")

# 2. every script compiles (fx_lib needs Fusion's adsk module, so it is compiled, not imported)
for dirpath, _, files in os.walk(ROOT):
    if ".git" in dirpath or "_work" in dirpath:
        continue
    for f in files:
        if f.endswith(".py"):
            py_compile.compile(os.path.join(dirpath, f), cfile=os.path.join(tempfile.gettempdir(), "x.pyc"), doraise=True)
ok("python files compile")

# 3. project scaffold
with tempfile.TemporaryDirectory() as td:
    subprocess.check_call([sys.executable, os.path.join(S, "new_project.py"), "Smoke Part", "--mode", "showcase", "--dir", td],
                          stdout=subprocess.DEVNULL)
    p = json.load(open(os.path.join(td, "smoke-part", "project.json")))
    if p["mode"] != "showcase":
        fail("new_project.py")
ok("new_project.py scaffolds a project")

# 4. live Fusion builds of both examples (optional, each opens a new unsaved document)
if subprocess.call([sys.executable, os.path.join(S, "check_setup.py")], stdout=subprocess.DEVNULL) == 0:
    for ex in ("monster-can-holder", "acrylic-keychain"):
        r = subprocess.run([sys.executable, os.path.join(S, "fusion_mcp.py"), "run",
                            os.path.join(ROOT, "examples", ex, "build.py"), "--lib"], capture_output=True, text=True)
        if r.returncode != 0 or "problems: 0" not in r.stdout:
            fail("live build of " + ex + ":" + chr(10) + r.stdout + r.stderr)
        ok("live Fusion build of " + ex + ": 0 timeline problems")
else:
    print("SKIP live Fusion builds (MCP server not reachable)")
print("smoke test passed")
