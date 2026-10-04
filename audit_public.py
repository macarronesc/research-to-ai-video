"""Offline publication audit. Reports locations and categories, never secret values."""

import ast
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
SECRET_PATTERNS = {
    "Google API credential": rb"AIza[0-9A-Za-z_-]{35}",
    "Telegram credential": rb"\b[0-9]{6,12}:[A-Za-z0-9_-]{30,50}\b",
    "OAuth refresh credential": rb"1//[0-9A-Za-z_-]{20,}",
    "OAuth access credential": rb"ya29\.[0-9A-Za-z_-]{20,}",
    "GitHub credential": rb"(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})",
    "AWS credential": rb"(?:AKIA|ASIA)[A-Z0-9]{16}",
    "private key": rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "credentials in URL": rb"https?://[^\s/\"'<>@:]+:[^\s/\"'<>@]+@",
    "literal JSON credential": rb'''(?i)["'](?:refresh_token|client_secret|api_key|access_token)["']\s*:\s*["'][^"']{12,}["']''',
}


def findings(data):
    return [category for category, pattern in SECRET_PATTERNS.items() if re.search(pattern, data)]


def git(*arguments):
    return subprocess.check_output(["git", "-C", str(ROOT), *arguments], stderr=subprocess.DEVNULL)


def audit():
    failures = []
    allowlist = {line[2:] for line in (ROOT / ".gitignore").read_text().splitlines()
                 if line.startswith("!/") and not line.endswith("/")}
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT).as_posix()
        if relative == ".git" and path.is_symlink():
            failures.append((relative, "symlinked Git directory not allowed"))
        if relative == ".git" or relative.startswith(".git/"):
            continue
        if path.is_symlink():
            failures.append((relative, "symlink not allowed"))
        elif path.is_file():
            if relative not in allowlist:
                failures.append((relative, "unreviewed/private file not allowed"))
            data = path.read_bytes()
            failures.extend((relative, category) for category in findings(data))
            try:
                text = data.decode("utf-8")
                if path.suffix == ".py":
                    ast.parse(text, filename=relative)
                if path.suffix == ".json":
                    json.loads(text)
            except (UnicodeError, SyntaxError, ValueError):
                failures.append((relative, "non-text or invalid source/example"))
    example = ROOT / ".env.example"
    for line in example.read_text().splitlines():
        if line and not line.startswith("#"):
            name, _, value = line.partition("=")
            if name not in {"GEMINI_API_KEY", "GEMINI_MODEL", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"}:
                failures.append((".env.example", "unknown environment variable"))
            if name != "GEMINI_MODEL" and value.strip():
                failures.append((".env.example", "credential placeholders must be empty"))
    config = ROOT / ".git/config"
    if config.exists():
        failures.extend((".git/config", category) for category in findings(config.read_bytes()))
    blob_count = 0
    try:
        git("rev-parse", "--git-dir")
        objects = git("cat-file", "--batch-all-objects", "--batch-check=%(objectname) %(objecttype)")
        objects = [line.split() for line in objects.decode().splitlines()]
        roots = {git("cat-file", "commit", oid).splitlines()[0].split()[1].decode()
                 for oid, kind in objects if kind == "commit"}
        for oid, kind in objects:
            if kind == "blob":
                blob_count += 1
                failures.extend(("Git blob " + oid[:12], category)
                                for category in findings(git("cat-file", "blob", oid)))
            elif kind == "tree":
                for entry in git("ls-tree", "-rz", "--full-tree", oid).split(b"\0"):
                    if entry:
                        details, name = entry.split(b"\t", 1)
                        historical = name.decode("utf-8", errors="replace")
                        permitted = historical in allowlist or (oid not in roots and any(
                            allowed.endswith("/" + historical) for allowed in allowlist))
                        if not permitted or details.startswith(b"120000 "):
                            failures.append(("Git tree " + oid[:12], "unreviewed historical path or symlink"))
        for entry in git("ls-files", "--stage", "-z").split(b"\0"):
            if entry:
                details, name = entry.split(b"\t", 1)
                if name.decode() not in allowlist or details.startswith(b"120000 "):
                    failures.append(("Git index", "unreviewed path or symlink"))
    except subprocess.CalledProcessError:
        failures.append(("Git", "cannot complete the Git object/index audit"))
    if failures:
        for location, category in sorted(set(failures)):
            print(f"FAIL {json.dumps(location)}: {category}")
        return 1
    print(f"PASS: working files, examples, syntax, index and all {blob_count} local Git blobs checked.")
    print("No unreviewed historical files or recognized secret patterns found.")
    print("This audit does not prove account revocation, service compliance or absence of all secret formats.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(audit())
    except Exception:
        print("FAIL: audit could not finish; details suppressed to avoid leaking private data.")
        sys.exit(1)
