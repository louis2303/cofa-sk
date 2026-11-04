#!/usr/bin/env python3
"""Inspect CSV / JSON rows: columns, missing values, duplicates, numeric ratios."""
import argparse
import csv
import json
from pathlib import Path
import sys

def is_number(v):
    if isinstance(v, bool):
        return False
    try:
        float(v)
        return True
    except (ValueError, TypeError, OverflowError):
        return False

def profile(path, limit=100000):
    if limit < 1:
        raise ValueError("max rows must be positive")
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise ValueError("CSV header is missing")
            fields = reader.fieldnames
            rows = []
            for idx, row in enumerate(reader):
                if idx >= limit:
                    raise ValueError("max rows exceeded; increase --max-rows")
                if None in row:
                    raise ValueError("CSV has extra unnamed columns")
                rows.append(row)
    elif path.suffix.lower() == ".json":
        with path.open(encoding="utf-8-sig") as f:
            rows = json.load(f)
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError("JSON root must be an array of objects")
        if len(rows) > limit:
            raise ValueError("max rows exceeded; increase --max-rows")
        fields = list(dict.fromkeys(k for row in rows for k in row))
    else:
        raise ValueError("only CSV and JSON are supported")
    missing = {}
    numeric = {}
    for field in fields:
        values = [row.get(field) for row in rows]
        missing[field] = sum(v is None or (isinstance(v, str) and not v.strip()) for v in values)
        nonempty = [v for v in values if v is not None and not (isinstance(v, str) and not v.strip())]
        count = sum(is_number(v) for v in nonempty)
        numeric[field] = {"numeric_count": count, "nonempty_count": len(nonempty),
                          "numeric_ratio": round(count / len(nonempty), 4) if nonempty else None}
    keys = [json.dumps(row, sort_keys=True, ensure_ascii=False, default=str) for row in rows]
    return {"file": path.name, "row_count": len(rows), "columns": fields, "missing": missing,
            "duplicate_rows": len(keys) - len(set(keys)), "numeric": numeric}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--max-rows", type=int, default=100000)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(profile(args.file, args.max_rows), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, csv.Error) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
