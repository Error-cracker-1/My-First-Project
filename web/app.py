"""
Minimal Flask web interface for the Daily AI Review project.

Run with:
    python -m web.app

Behavior summary:
- Reuses scripts.ai_review in-process when importable (preferred).
- Falls back to running "python -m scripts.ai_review <mode>" in a subprocess.
- Stores minimal state in web/.web_review_state.json and log in web/review.log.
- Serves: / (home), /run-review (POST), /status, /reports, /reports/view/<name>, /ai_report, /dashboard.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import (
    Flask,
    abort,
    jsonify,
    render_template,
    request,
    send_file,
)

WEB_DIR = Path(__file__).parent
STATE_FILE = WEB_DIR / ".web_review_state.json"
LOG_FILE = WEB_DIR / "review.log"
REPORTS_DIR = Path.cwd() / "reports"
AI_REPORT = Path.cwd() / "AI_REPORT.md"
# Use existing dashboard path inside reports/ (per your instruction)
DASHBOARD_HTML = Path.cwd() / "reports" / "dashboard.html"

app = Flask(
    __name__,
    static_folder=str(WEB_DIR / "static"),
    template_folder=str(WEB_DIR / "templates"),
)

# Try importing the existing review module for in-process execution.
try:
    from scripts.ai_review import main as review_main  # type: ignore
    _CAN_RUN_IN_PROCESS = True
except Exception:
    review_main = None
    _CAN_RUN_IN_PROCESS = False


def _read_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _write_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, default=str), encoding="utf-8")


def _append_log(line: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(line.rstrip() + "\n")


def _start_review_in_thread(mode: str) -> None:
    """Start review in a background thread (in-process preferred)."""

    def _run():
        state = {
            "running": True,
            "mode": mode,
            "start_time": datetime.utcnow().isoformat() + "Z",
            "pid": None,
            "exit_code": None,
        }
        _write_state(state)

        try:
            if _CAN_RUN_IN_PROCESS and review_main is not None:
                # Run in-process by temporarily adjusting sys.argv so existing CLI logic works.
                _append_log(f"Starting in-process review (mode={mode})")
                import sys

                old_argv = sys.argv[:]
                sys.argv = [sys.argv[0], mode]
                try:
                    review_main()
                    _append_log("Review completed (in-process)")
                    state["exit_code"] = 0
                except SystemExit as e:
                    _append_log(f"Review exited with SystemExit: {e}")
                    state["exit_code"] = getattr(e, "code", 1)
                except Exception as e:
                    _append_log(f"Review failed: {e}")
                    state["exit_code"] = 2
                finally:
                    sys.argv = old_argv
            else:
                # Subprocess fallback
                _append_log("Starting subprocess review")
                import subprocess

                proc = subprocess.Popen(
                    ["python", "-m", "scripts.ai_review", mode],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                state["pid"] = proc.pid
                _write_state(state)

                assert proc.stdout is not None
                for line in proc.stdout:
                    _append_log(line)
                proc.wait()
                state["exit_code"] = proc.returncode
                _append_log(f"Subprocess exited with {proc.returncode}")
        finally:
            state["running"] = False
            state["end_time"] = datetime.utcnow().isoformat() + "Z"
            _write_state(state)

    t = threading.Thread(target=_run, daemon=True)
    t.start()


@app.route("/")
def index():
    repo_name = Path.cwd().name

    # get current branch
    try:
        import subprocess

        branch = (
            subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            .stdout.strip()
        )
    except Exception:
        branch = "unknown"

    state = _read_state()

    # last review timestamp: prefer state end_time, else most recent report file
    last_review: Optional[str] = None
    if state.get("end_time"):
        last_review = state.get("end_time")
    else:
        if REPORTS_DIR.exists():
            files = sorted(REPORTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
            if files:
                last_review = datetime.utcfromtimestamp(files[0].stat().st_mtime).isoformat() + "Z"

    # repository statistics: try to reuse scripts.repository.get_git_tracked_files
    files_discovered = 0
    try:
        from scripts.repository import get_git_tracked_files  # type: ignore

        files_discovered = len(get_git_tracked_files("all"))
    except Exception:
        # fallback to git ls-files
        try:
            import subprocess

            out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout
            files_discovered = len([l for l in out.splitlines() if l.strip()])
        except Exception:
            files_discovered = 0

    # repo health: attempt to use calculate_repository_health (best-effort)
    repo_health = None
    try:
        from scripts.report import calculate_repository_health  # type: ignore

        # naive defaults if no parsed report
        changed = 0
        failed = 0
        # try parsing latest report for numbers
        if REPORTS_DIR.exists():
            latest = next(REPORTS_DIR.glob("*.md"), None)
            if latest:
                text = latest.read_text(encoding="utf-8")
                for line in text.splitlines():
                    if line.startswith("Files Changed"):
                        try:
                            changed = int(line.split(":", 1)[1].strip())
                        except Exception:
                            pass
                    if line.startswith("Files Failed"):
                        try:
                            failed = int(line.split(":", 1)[1].strip())
                        except Exception:
                            pass

        repo_health = calculate_repository_health(changed, failed)
    except Exception:
        repo_health = None

    return render_template(
        "index.html",
        repo_name=repo_name,
        branch=branch,
        last_review=last_review,
        files_discovered=files_discovered,
        repo_health=repo_health,
        state=state,
    )


@app.route("/run-review", methods=["POST"])
def run_review():
    data = request.get_json() or {}
    mode = data.get("mode") or request.args.get("mode") or "modified"

    state = _read_state()
    if state.get("running"):
        return jsonify({"started": False, "reason": "already_running"}), 409

    _start_review_in_thread(mode)
    return jsonify({"started": True, "mode": mode})


@app.route("/status")
def status():
    state = _read_state()
    tail = []
    if LOG_FILE.exists():
        try:
            with LOG_FILE.open("r", encoding="utf-8") as fh:
                lines = fh.read().splitlines()
                tail = lines[-300:]
        except Exception:
            tail = ["<could not read log>"]
    return jsonify({"state": state, "log": tail})


@app.route("/reports")
def list_reports():
    if not REPORTS_DIR.exists():
        return render_template("reports.html", reports=[])
    entries = []
    for p in sorted(REPORTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
        entries.append({"name": p.name, "path": str(p), "date": datetime.utcfromtimestamp(p.stat().st_mtime).isoformat() + "Z"})
    return render_template("reports.html", reports=entries)


@app.route("/reports/view/<path:filename>")
def view_report(filename: str):
    p = REPORTS_DIR / filename
    if not p.exists() or not p.is_file():
        abort(404)
    text = p.read_text(encoding="utf-8")
    try:
        import markdown

        html = markdown.markdown(text, extensions=["fenced_code", "tables"])  # type: ignore
        return render_template("report_view.html", content=html, filename=filename)
    except Exception:
        return render_template("report_view.html", content=f"<pre>{text}</pre>", filename=filename)


@app.route("/ai_report")
def ai_report():
    if not AI_REPORT.exists():
        abort(404)
    text = AI_REPORT.read_text(encoding="utf-8")
    try:
        import markdown

        html = markdown.markdown(text, extensions=["fenced_code", "tables"])  # type: ignore
        return render_template("report_view.html", content=html, filename=AI_REPORT.name)
    except Exception:
        return render_template("report_view.html", content=f"<pre>{text}</pre>", filename=AI_REPORT.name)


@app.route("/dashboard")
def dashboard():
    if not DASHBOARD_HTML.exists():
        return render_template("dashboard.html", dashboard_exists=False)
    return send_file(DASHBOARD_HTML)


if __name__ == "__main__":
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        _write_state({"running": False})
    if not LOG_FILE.exists():
        LOG_FILE.write_text("", encoding="utf-8")
    app.run(host="127.0.0.1", port=5000)
