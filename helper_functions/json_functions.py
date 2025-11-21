# Import 
import os
import json
import time
from pathlib import Path

#define read json safely - resolves the issue of Crew AI running and missing the JSON file that is still being built 
def read_json_safely(path, retries=5, delay=1):
    p = Path(path)
    for attempt in range(1, retries + 1):
        if not p.exists():
            print(f"⚠️ {p} not found (attempt {attempt}/{retries})...")
            time.sleep(delay)
            continue

        text = p.read_text(encoding="utf-8").strip()
        if not text:
            print(f"⚠️ {p} empty (attempt {attempt}/{retries})...")
            time.sleep(delay)
            continue

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print(f"⚠️ {p} invalid JSON (attempt {attempt}/{retries})...")
            time.sleep(delay)
    raise ValueError(f"❌ Failed to read valid JSON from {p}")

#write json
def write_json(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

#time lag to wait for json files to be created before proceeding to the next step
def wait_for_file(path, timeout=10):
    start = time.time()
    while True:
        if os.path.exists(path) or os.path.getsize(path) > 0:
            try:
                with open(path, encoding="utf-8") as f:
                    json.load(f)  
                return
            except Exception:
                pass
        if time.time() - start > timeout: 
            raise TimeoutError(f"{path} not ready after {timeout}s")
        time.sleep(0.5)

#clean output in between each runs so that the json files are not corrupted (Step 0)
def cleanup_output():
    """Delete old or empty JSON files from previous runs."""
    output_dir = Path("output")
    if not output_dir.exists():
        return

    for f in output_dir.glob("*.json"):
        try:
            # Remove if empty, whitespace-only, or stale
            text = f.read_text(encoding="utf-8").strip()
            if not text:
                print(f"🧹 Removing empty or stale file: {f}")
                f.unlink(missing_ok=True)
            else:
                print(f"🧹 Cleared old file: {f}")
                f.unlink(missing_ok=True)
        except Exception as e:
            print(f"⚠️ Skipped cleanup for {f}: {e}")