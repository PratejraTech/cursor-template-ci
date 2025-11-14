#!/usr/bin/env python3
"""
Simple state updater for Achilles + Cursor intelligence logging.

Usage (local / manual):

  # Mark backend phase 1 in progress
  python tools/update_state.py state/backend_state.mdc backend_phase_1 in_progress

  # Mark backend phase 1 done, make it current, and append intelligence entry
  python tools/update_state.py state/backend_state.mdc backend_phase_1 done --make-current

Usage (CI with overwrite of signals):

  python tools/update_state.py \
    state/backend_state.mdc backend_phase_1 done \
    --make-current \
    --tests-passed \
    --warnings 1 \
    --errors 0 \
    --summary "Backend data foundations built; unit tests green with 1 minor warning."
"""

import argparse
from pathlib import Path
from datetime import datetime, timezone

import yaml  # requires: pip install pyyaml

ALLOWED_STATUS = {"not_started", "in_progress", "done", "blocked"}
CURSOR_INTEL_PATH = Path("state/cursor_intel.mdc")


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) if text.strip() else {}
    return data or {}


def save_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def update_state_file(state_file: Path, phase_id: str, status: str, make_current: bool):
    data = load_yaml(state_file)

    phases = data.get("phases")
    if not isinstance(phases, dict):
        raise SystemExit(f"'phases' mapping not found in {state_file}")

    if phase_id not in phases:
        raise SystemExit(f"Phase '{phase_id}' not found in {state_file}")

    if status not in ALLOWED_STATUS:
        raise SystemExit(
            f"Status '{status}' not allowed. Use one of: {', '.join(sorted(ALLOWED_STATUS))}"
        )

    old_status = phases[phase_id].get("status")
    phases[phase_id]["status"] = status
    data["phases"] = phases

    if make_current:
        data["current_phase"] = phase_id

    save_yaml(state_file, data)

    phase_name = phases[phase_id].get("name", phase_id)
    return old_status, phase_name


def guess_subsystem(state_file: Path) -> str:
    name = state_file.name.lower()
    if "backend" in name:
        return "backend"
    if "nextjs" in name or "frontend" in name:
        return "frontend"
    return "unknown"


def upsert_cursor_intel_entry(
    subsystem: str,
    phase_id: str,
    phase_name: str,
    status: str,
    tests_passed: bool | None,
    warnings: int | None,
    errors: int | None,
    summary: str | None,
):
    data = load_yaml(CURSOR_INTEL_PATH)
    entries = data.get("entries")
    if not isinstance(entries, list):
        entries = []

    # Find existing entry for this subsystem+phase_id
    idx = None
    for i, entry in enumerate(entries):
        if entry.get("subsystem") == subsystem and entry.get("phase_id") == phase_id:
            idx = i
            break

    now = datetime.now(timezone.utc).isoformat()

    # Defaults for signals
    default_signals = {
        "tests_passed": False,
        "warnings": 0,
        "errors": 0,
    }

    if idx is not None:
        # Update existing entry (CI overwrite behavior)
        entry = entries[idx]
        signals = entry.get("signals") or {}
        signals.setdefault("tests_passed", default_signals["tests_passed"])
        signals.setdefault("warnings", default_signals["warnings"])
        signals.setdefault("errors", default_signals["errors"])
    else:
        # Create new entry
        entry = {
            "subsystem": subsystem,
            "phase_id": phase_id,
            "phase_name": phase_name,
            "status": status,
            "timestamp": now,
            "signals": default_signals.copy(),
            "summary": summary or f"Phase {phase_id} ({phase_name}) marked as {status}.",
        }
        signals = entry["signals"]
        entries.append(entry)

    # Overwrite fields based on CI inputs (if provided)
    if tests_passed is not None:
        signals["tests_passed"] = bool(tests_passed)
    if warnings is not None:
        signals["warnings"] = int(warnings)
    if errors is not None:
        signals["errors"] = int(errors)

    entry["signals"] = signals
    entry["status"] = status
    entry["phase_name"] = phase_name
    entry["timestamp"] = now
    if summary:
        entry["summary"] = summary

    data["entries"] = entries
    save_yaml(CURSOR_INTEL_PATH, data)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Update Achilles state file and Cursor intelligence log."
    )
    parser.add_argument("state_file", type=Path, help="Path to backend_state.mdc or nextjs_state.mdc")
    parser.add_argument("phase_id", type=str, help="Phase identifier, e.g. backend_phase_1")
    parser.add_argument("status", type=str, help="Phase status (not_started|in_progress|done|blocked)")
    parser.add_argument(
        "--make-current",
        action="store_true",
        help="Set this phase as current_phase in the state file.",
    )

    # CI / signals flags (optional)
    parser.add_argument(
        "--tests-passed",
        action="store_true",
        help="Mark tests_passed=True for this phase in cursor_intel.mdc.",
    )
    parser.add_argument(
        "--warnings",
        type=int,
        default=None,
        help="Number of warnings for this phase (overwrites existing entry).",
    )
    parser.add_argument(
        "--errors",
        type=int,
        default=None,
        help="Number of errors for this phase (overwrites existing entry).",
    )
    parser.add_argument(
        "--summary",
        type=str,
        default=None,
        help="Short summary for this phase (overwrites existing entry).",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if not args.state_file.exists():
        raise SystemExit(f"State file not found: {args.state_file}")

    old_status, phase_name = update_state_file(
        state_file=args.state_file,
        phase_id=args.phase_id,
        status=args.status,
        make_current=args.make_current,
    )

    print(
        f"Updated {args.state_file}: phase '{args.phase_id}' status = '{args.status}'"
        + (" and set as current_phase" if args.make_current else "")
    )

    # If we just set this phase to done, update Cursor intel
    if args.status == "done":
        subsystem = guess_subsystem(args.state_file)

        # tests_passed flag: if provided, True; if not, leave as None (no change if entry exists)
        tests_passed = True if args.tests_passed else None

        upsert_cursor_intel_entry(
            subsystem=subsystem,
            phase_id=args.phase_id,
            phase_name=phase_name,
            status=args.status,
            tests_passed=tests_passed,
            warnings=args.warnings,
            errors=args.errors,
            summary=args.summary,
        )

        print(
            f"Cursor intel updated for subsystem='{subsystem}', phase='{args.phase_id}' in {CURSOR_INTEL_PATH}"
        )


if __name__ == "__main__":
    main()
    