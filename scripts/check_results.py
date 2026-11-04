#!/usr/bin/env python3
"""Check a test-evidence manifest and output files. Does not execute tests."""
import argparse
import json
from pathlib import Path
import sys

def check(manifest, root):
    checks = manifest.get("checks")
    if not isinstance(checks, list) or not checks:
        return {"status": "FAIL", "reasons": ["No executed checks recorded"]}
    errors = []
    for idx, c in enumerate(checks):
        if not isinstance(c, dict) or not c.get("command"):
            errors.append(f"check {idx}: missing command")
            continue
        count = c.get("test_count")
        if type(count) is not int or count < 1:
            errors.append(f"check {idx}: test_count must be >= 1")
        if type(c.get("exit_code")) is not int or c["exit_code"] != 0:
            errors.append(f"check {idx}: nonzero or missing exit_code")
        if c.get("status") != "passed":
            errors.append(f"check {idx}: not passed")
    outputs = manifest.get("required_outputs", [])
    if not isinstance(outputs, list):
        errors.append("required_outputs must be a list")
    else:
        for item in outputs:
            if not isinstance(item, str) or not item.strip():
                errors.append("invalid output path")
                continue
            target = (root / item).resolve()
            if not target.is_relative_to(root.resolve()):
                errors.append(f"unsafe output path: {item}")
            elif not target.is_file():
                errors.append(f"missing output: {item}")
    return {"status": "FAIL" if errors else "PASS", "reasons": errors,
            "note": "Manifest/file checks only; cannot prove tests were actually run or correct"}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        with args.manifest.open(encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("manifest must be an object")
        result = check(data, args.root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
