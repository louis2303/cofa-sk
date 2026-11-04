#!/usr/bin/env python3
"""Check basic tools and workspace safely. No external dependencies."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile

def inspect(root):
    results = []
    for tool in ("python", "node", "npm", "git"):
        found = shutil.which(tool)
        results.append({"check": "tool:" + tool, "status": "PASS" if found else "WARN", "detail": found or "not on PATH"})
    results.append({"check": "python_version", "status": "PASS", "detail": sys.version.split()[0]})
    if not root.is_dir():
        results.append({"check": "root", "status": "FAIL", "detail": "directory not found"})
        return results
    try:
        with tempfile.NamedTemporaryFile(prefix=".preflight-", dir=root, delete=True) as f:
            f.write(b"ok")
            f.flush()
        results.append({"check": "write_permission", "status": "PASS", "detail": "temporary write worked"})
    except OSError as exc:
        results.append({"check": "write_permission", "status": "FAIL", "detail": str(exc)})
    for name in ("README.md", "AGENTS.md", "package.json", "pyproject.toml", "requirements.txt", ".agents/skills"):
        results.append({"check": "present:" + name, "status": "INFO", "detail": (root / name).exists()})
    return results

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    checks = inspect(args.root)
    print(json.dumps({"root": str(args.root), "checks": checks}, ensure_ascii=False, indent=2))
    return 1 if any(c["status"] == "FAIL" for c in checks) else 0

if __name__ == "__main__":
    sys.exit(main())
