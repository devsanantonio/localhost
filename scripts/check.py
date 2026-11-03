"""Run every starter against its live source and record which answered.

    python3 scripts/check.py           # prints a table, writes data/status.json
                                       # exits 1 if any starter failed

Each starter runs with --json, the way an agent or an Action would, and passes
if it exits cleanly with valid JSON. The weekly GitHub Action runs this and opens
an issue when something breaks, usually because a publisher changed a field.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Each starter, the arguments that exercise it, and the publishers it depends on.
CASES = [
    ("311-by-district", [], ["City of San Antonio"]),
    ("permits-near-you", ["--meters", "60"], ["City of San Antonio"]),
    ("how-we-compare", ["--owners"], ["City of San Antonio"]),
    ("acequias", [], ["Bexar County"]),
    ("san-antonio-1897", [], ["Bexar County"]),
    ("via-next-bus", ["houston & st mary", "--count", "3"], ["VIA Metropolitan Transit"]),
    ("creek-levels", ["--near", "29.3270,-98.4500"], ["U.S. Geological Survey", "San Antonio River Authority"]),
    ("aquifer-today", [], ["Edwards Aquifer Authority", "U.S. Geological Survey"]),
    ("funded-projects", [], ["Alamo Area MPO"]),
    ("funded-projects", ["--flooding"], ["Alamo Area MPO"]),
    ("low-water-crossings", [], ["Opportunity Home San Antonio"]),
    ("peek", ["--find", "flood"], ["City of San Antonio", "Bexar County", "San Antonio River Authority", "Alamo Area MPO",
                                   "Opportunity Home San Antonio", "Edwards Aquifer Authority"]),
]


def run(name, args):
    started = time.time()
    try:
        done = subprocess.run([sys.executable, os.path.join(ROOT, "starters", name, "main.py"), *args, "--json"],
                              capture_output=True, text=True, timeout=300, cwd=os.path.join(ROOT, "starters", name))
        if done.returncode != 0:
            raise RuntimeError((done.stderr or done.stdout).strip().splitlines()[-1] if (done.stderr or done.stdout).strip()
                               else f"exited with {done.returncode}")
        json.loads(done.stdout)
        error = None
    except Exception as e:
        error = f"{type(e).__name__}: {e}"[:500]
    return {"starter": name, "args": args, "ok": error is None, "seconds": round(time.time() - started, 1), "error": error}


if __name__ == "__main__":
    results = [dict(run(name, args), publishers=pubs) for name, args, pubs in CASES]
    publishers = {}
    for r in results:
        for p in r["publishers"]:
            publishers[p] = publishers.get(p, True) and r["ok"]
    status = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ok": all(r["ok"] for r in results),
        "publishers": [{"publisher": p, "ok": ok} for p, ok in publishers.items()],
        "starters": results,
    }
    with open(os.path.join(ROOT, "data", "status.json"), "w") as f:
        json.dump(status, f, indent=2)
        f.write("\n")

    for r in results:
        print(f"{'ok  ' if r['ok'] else 'FAIL'}  {r['seconds']:>5}s  {r['starter']} {' '.join(r['args'])}"
              + (f"\n        {r['error']}" if r["error"] else ""))
    sys.exit(0 if status["ok"] else 1)
