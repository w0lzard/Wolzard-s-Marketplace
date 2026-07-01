#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

VAULT = Path("/home/wolzard/Projects/Obsidian Vault")
LOG_DIR = VAULT / "Claude Code Logs"
TEMP_DIR = Path("/tmp")


def safe_truncate(s: str, n: int = 400) -> str:
    if not s:
        return ""
    s = s.strip()
    return s[:n] + "\n…[truncated]" if len(s) > n else s


def get_project(file_path: str) -> str:
    try:
        p = Path(file_path)
        parts = p.parts
        for marker in ("Projects", "projects"):
            if marker in parts:
                idx = parts.index(marker)
                if idx + 1 < len(parts):
                    return parts[idx + 1]
        home = Path.home()
        try:
            rel = p.relative_to(home)
            if rel.parts:
                return rel.parts[0]
        except ValueError:
            pass
        return p.parent.name or "General"
    except Exception:
        return "General"


def ensure_note(note_path: Path, date_str: str):
    note_path.parent.mkdir(parents=True, exist_ok=True)
    if not note_path.exists():
        note_path.write_text(
            f"---\ndate: {date_str}\ntags: [claude-code, dev-log]\n---\n\n"
            f"# Claude Code Log — {date_str}\n\n",
            encoding="utf-8",
        )


def append_note(note_path: Path, text: str):
    with open(note_path, "a", encoding="utf-8") as f:
        f.write(text)


def track_session(session_id: str, entry: dict):
    session_file = TEMP_DIR / f"claude-obsidian-{session_id}.json"
    entries = []
    if session_file.exists():
        try:
            entries = json.loads(session_file.read_text())
        except Exception:
            entries = []
    entries.append(entry)
    session_file.write_text(json.dumps(entries, indent=2))


def is_own_file(file_path: str) -> bool:
    """Skip writes to the log directory or hook scripts themselves."""
    try:
        p = Path(file_path).resolve()
        return str(LOG_DIR.resolve()) in str(p) or str(Path("/home/wolzard/.claude").resolve()) in str(p)
    except Exception:
        return False


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        data = json.loads(raw)
    except Exception:
        return

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    tool_response = data.get("tool_response", {})
    session_id = data.get("session_id", "unknown")

    now = datetime.now()
    ts = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")

    entry = {"tool": tool_name, "time": ts}
    note_block = None
    project = None

    if tool_name == "Edit":
        file_path = tool_input.get("file_path", "")
        if is_own_file(file_path):
            return
        old_str = tool_input.get("old_string", "")
        new_str = tool_input.get("new_string", "")
        project = get_project(file_path)
        entry.update({"file": file_path, "project": project})

        note_block = (
            f"### ✏️ {ts} — Edit · `{Path(file_path).name}`\n"
            f"**File:** `{file_path}`  \n"
            f"**Project:** {project}\n\n"
            f"**Removed:**\n```\n{safe_truncate(old_str)}\n```\n\n"
            f"**Added:**\n```\n{safe_truncate(new_str)}\n```\n\n"
        )

    elif tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        if is_own_file(file_path):
            return
        content = tool_input.get("content", "")
        project = get_project(file_path)
        entry.update({"file": file_path, "project": project})

        note_block = (
            f"### 📝 {ts} — Write · `{Path(file_path).name}`\n"
            f"**File:** `{file_path}`  \n"
            f"**Project:** {project}\n\n"
            f"**Content preview:**\n```\n{safe_truncate(content, 500)}\n```\n\n"
        )

    elif tool_name == "Bash":
        command = tool_input.get("command", "").strip()
        description = tool_input.get("description", "")

        skip_prefixes = [
            "ls", "cat ", "find ", "grep ", "which ", "echo ", "pwd",
            "git log", "git status", "git diff", "head ", "tail ", "wc ",
            "python3 /home/wolzard/.claude/scripts/",  # don't log our own hooks
        ]
        if any(command.startswith(p) for p in skip_prefixes):
            return

        output = ""
        if isinstance(tool_response, dict):
            output = tool_response.get("output", "") or str(tool_response)
        elif isinstance(tool_response, str):
            output = tool_response

        project = "General"
        entry.update({"command": command, "project": project})

        note_block = (
            f"### 🖥️ {ts} — Command\n"
            f"**Command:** `{command}`  \n"
            f"**Description:** {description}\n\n"
            f"**Output:**\n```\n{safe_truncate(output, 400)}\n```\n\n"
        )

    if not note_block:
        return

    daily_note = LOG_DIR / "Daily" / f"{date_str}.md"
    ensure_note(daily_note, date_str)
    append_note(daily_note, note_block)

    if project and project != "General":
        proj_note = LOG_DIR / "Projects" / project / f"{date_str}.md"
        ensure_note(proj_note, date_str)
        append_note(proj_note, note_block)

    track_session(session_id, entry)


if __name__ == "__main__":
    main()
