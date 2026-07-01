#!/usr/bin/env python3
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

VAULT = Path("/home/wolzard/Projects/Obsidian Vault")
LOG_DIR = VAULT / "Claude Code Logs"
TEMP_DIR = Path("/tmp")


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        data = json.loads(raw)
    except Exception:
        return

    if data.get("stop_hook_active"):
        return

    session_id = data.get("session_id", "unknown")
    session_file = TEMP_DIR / f"claude-obsidian-{session_id}.json"

    if not session_file.exists():
        return

    try:
        entries = json.loads(session_file.read_text())
    except Exception:
        return

    if not entries:
        return

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    end_ts = now.strftime("%H:%M:%S")

    start_ts = entries[0].get("time", end_ts)

    projects: dict[str, list[str]] = defaultdict(list)
    files_changed: list[tuple[str, str, str]] = []
    commands_run: list[tuple[str, str]] = []

    for entry in entries:
        tool = entry.get("tool", "")
        proj = entry.get("project", "General")
        t = entry.get("time", "")

        if tool in ("Edit", "Write"):
            fp = entry.get("file", "")
            projects[proj].append(f"{tool}: `{Path(fp).name}`")
            files_changed.append((t, fp, tool))
        elif tool == "Bash":
            cmd = entry.get("command", "")
            commands_run.append((t, cmd))

    lines = [
        f"---\ndate: {date_str}\ntags: [claude-code, session-summary]\n---\n\n",
        f"# Session Summary — {date_str} {time_str}\n\n",
        f"> **Duration:** {start_ts} → {end_ts}\n\n",
    ]

    real_projects = [p for p in projects if p not in ("General",)]
    if real_projects:
        lines.append("## Projects\n\n")
        for proj in real_projects:
            n = len([e for e in entries if e.get("project") == proj])
            lines.append(f"- **{proj}** — {n} change{'s' if n != 1 else ''}\n")
        lines.append("\n")

    if files_changed:
        lines.append("## Files Changed\n\n")
        lines.append("| Time | File | Action |\n")
        lines.append("|------|------|--------|\n")
        for t, fp, action in files_changed:
            lines.append(f"| `{t}` | `{Path(fp).name}` | {action} |\n")
        lines.append("\n")

    if commands_run:
        lines.append("## Commands Run\n\n")
        for t, cmd in commands_run:
            lines.append(f"- `{t}` — `{cmd[:100]}`\n")
        lines.append("\n")

    lines.append(f"> Full change details: [[Daily/{date_str}]]\n")

    summary = "".join(lines)

    session_dir = LOG_DIR / "Sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    session_note = session_dir / f"{date_str}-{time_str.replace(':', '-')}.md"
    session_note.write_text(summary, encoding="utf-8")

    daily_note = LOG_DIR / "Daily" / f"{date_str}.md"
    if daily_note.exists():
        with open(daily_note, "a", encoding="utf-8") as f:
            f.write(
                f"\n---\n\n## Session ended {end_ts}\n"
                f"→ [[Sessions/{session_note.stem}]]\n\n"
            )

    try:
        session_file.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    main()
