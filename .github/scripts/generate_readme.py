import os
import re
import subprocess
import time
from pathlib import Path

from google import genai
from google.genai import types

ROOT = Path.cwd()
README = ROOT / "README.md"
MODEL = "gemini-3.5-flash-lite"
EXCLUDED_DIRS = {".git", ".venv", "venv", "node_modules", "vendor", "build", "dist", "coverage", "__pycache__", ".cache", "target", "out", "generated"}
IGNORED_CHANGE_PREFIXES = {"README.md", ".github/scripts/generate_readme.py", ".github/readme-generator-instructions.md"}
SOURCE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".ps1", ".json", ".yml", ".yaml", ".toml", ".java", ".c", ".cpp", ".h", ".hpp", ".go", ".rs", ".rb", ".php", ".cs", ".md", ".txt"}
MANIFESTS = {"requirements.txt", "Requirements.txt", "pyproject.toml", "package.json", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "build.gradle.kts"}
BADGE_RE = re.compile(r"^\\s*\\[!\\[[^\\]]*\\]\\([^)]*/actions/workflows/[^)]*/badge\\.svg[^)]*\\)\\]\\([^)]*\\)\\s*$")

def git(*args):
    result = subprocess.run(["git", *args], capture_output=True, text=True, timeout=30, check=False)
    return result.stdout.strip()

def read(path, limit):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""

def changed_files():
    before = os.environ.get("BEFORE_SHA", "")
    sha = os.environ.get("GITHUB_SHA", "HEAD")
    if before and before != "0" * 40:
        raw = git("diff", "--name-only", before, sha, "--", ".", ":!README.md")
    else:
        raw = git("diff", "--name-only", "HEAD^", "HEAD", "--", ".", ":!README.md")
    return [p for p in raw.splitlines() if p]

def is_meaningful(path):
    if path in IGNORED_CHANGE_PREFIXES or path.startswith(".github/scripts/") or path.startswith(".git"):
        return False
    if any(part in EXCLUDED_DIRS for part in Path(path).parts):
        return False
    return Path(path).suffix.lower() in SOURCE_EXTENSIONS or path.startswith(".github/workflows/")

def workflow_badges():
    result = []
    workflows = ROOT / ".github" / "workflows"
    if not workflows.is_dir():
        return result
    branch = os.environ.get("TARGET_BRANCH", "AI-Chatbot")
    for path in sorted(workflows.iterdir()):
        if path.suffix.lower() not in {".yml", ".yaml"}:
            continue
        name = path.stem
        for line in read(path, 2000).splitlines():
            match = re.match(r"^name\\s*:\\s*(.+)$", line.strip())
            if match:
                name = match.group(1).strip().strip('"').strip("'")
                break
        filename = path.name
        result.append(f"[![{name}](https://github.com/Error-cracker-1/My-First-Project/actions/workflows/{filename}/badge.svg?branch={branch})](https://github.com/Error-cracker-1/My-First-Project/actions/workflows/{filename})")
    return result

def sync_badges(original, generated):
    badges = [line.strip() for line in original.splitlines() if BADGE_RE.match(line)]
    for badge in workflow_badges():
        if badge not in badges:
            badges.append(badge)
    lines = [line for line in generated.splitlines() if not BADGE_RE.match(line.strip())]
    heading = next((i for i, line in enumerate(lines) if line.strip().lower() == "## github actions"), None)
    if heading is None:
        insert_at = 1 if lines and lines[0].startswith("#") else 0
        lines[insert_at:insert_at] = ["", "## GitHub Actions", "", *badges, ""]
    else:
        end = heading + 1
        while end < len(lines) and not lines[end].startswith("## "):
            end += 1
        lines[heading + 1:end] = ["", *badges, ""]
    return "\n".join(lines).strip()

changes = changed_files()
meaningful = [p for p in changes if is_meaningful(p)]
if not meaningful:
    print("No README-relevant changes detected; skipping Gemini API call.")
    raise SystemExit(0)

file_list = sorted(meaningful)[:120]
evidence = []
for path_text in file_list[:25]:
    path = ROOT / path_text
    if path.is_file():
        evidence.append(f"--- {path_text} ---\\n{read(path, 5000)}")
manifest_text = []
for name in MANIFESTS:
    path = ROOT / name
    if path.is_file():
        manifest_text.append(f"--- {name} ---\\n{read(path, 5000)}")
current = read(README, 24000)
recent = git("log", "-6", "--oneline", "--decorate")
prompt = f"""Maintain README.md for this repository.

Rules:
- The repository is the source of truth.
- Use only information supported by the supplied evidence.
- Preserve useful existing README content.
- Do not invent features, commands, dependencies, URLs, workflows, or setup steps.
- Keep the README concise and useful.
- Do not expose secrets.
- Return ONLY the complete README.md.
- Keep existing valid GitHub Actions badges and ensure badges exist for workflows currently present.
- The target branch is AI-Chatbot.

Current README:
{current}

Changed paths:
{chr(10).join(file_list)}

Relevant file evidence:
{chr(10).join(evidence)}

Project manifests:
{chr(10).join(manifest_text)}

Recent commits:
{recent}
"""
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise SystemExit("GOOGLE_API_KEY is missing from repository secrets.")
client = genai.Client(api_key=api_key)
config = types.GenerateContentConfig(max_output_tokens=6000, candidate_count=1)
try:
    response = client.models.generate_content(model=MODEL, contents=prompt, config=config)
except Exception as exc:
    message = str(exc)
    if "429" in message or "RESOURCE_EXHAUSTED" in message:
        raise SystemExit("Gemini quota/rate limit reached. No retry was attempted to avoid consuming more quota.") from exc
    if "503" not in message and "UNAVAILABLE" not in message:
        raise
    time.sleep(5)
    response = client.models.generate_content(model=MODEL, contents=prompt, config=config)
generated = (response.text or "").strip()
if generated.startswith("```"):
    lines = generated.splitlines()[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    generated = "\n".join(lines).strip()
if len(generated) < 300:
    raise SystemExit("Generated README is suspiciously short; refusing to replace README.")
README.write_text(sync_badges(current, generated) + "\n", encoding="utf-8")
print(f"README updated using one {MODEL} request.")