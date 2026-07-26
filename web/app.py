from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

# Add vendor and lib folders to sys.path to ensure dependencies are found in any environment
BASE_DIR = Path(__file__).resolve().parent.parent
possible_vendor_dirs = [
    BASE_DIR / "vendor",
    BASE_DIR / "lib",
    Path.cwd() / "vendor",
    Path.cwd() / "lib",
    Path("/vendor"),
    Path("/lib"),
    Path("/usr/lib/python3/dist-packages"),
]
for target_dir in possible_vendor_dirs:
    if target_dir.exists() and str(target_dir) not in sys.path:
        sys.path.insert(0, str(target_dir))

from flask import (
    Flask,
    Response,
    abort,
    jsonify,
    render_template,
    request,
    send_file,
)

# --- Global Constants ---
WEB_DIR = Path(__file__).parent
STATE_FILE = WEB_DIR / ".web_review_state.json"
LOG_FILE = WEB_DIR / "review.log"
REPORTS_DIR = Path.cwd() / "reports"
AI_REPORT = Path.cwd() / "AI_REPORT.md"

app = Flask(
    __name__,
    static_folder=str(WEB_DIR / "static"),
    template_folder=str(WEB_DIR / "templates"),
)

# --- Dynamic imports for optional script functionality ---
# These imports are wrapped in try-except blocks to allow the web app
# to run even if the `scripts` modules are not available in the PYTHONPATH.

# The `_review_main` callable and `_CAN_RUN_IN_PROCESS` flag are currently unused,
# as the review process is always started in a subprocess for isolation and robust logging.
# They are kept as placeholders for potential future direct in-process execution.
_review_main: Optional[Callable[[], None]] = None
# _CAN_RUN_IN_PROCESS = False # Unused variable
try:
    from scripts.ai_review import main as _imported_review_main  # type: ignore[attr-defined, unused-ignore]
    _review_main = _imported_review_main
    # _CAN_RUN_IN_PROCESS = True # Unused variable
except ImportError:
    pass

try:
    from scripts.config import AVAILABLE_MODELS
except ImportError:
    AVAILABLE_MODELS = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.0-pro-exp",
        "gemini-2.0-flash-thinking-exp",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.0-pro",
    ]

_get_git_tracked_files: Optional[Callable[[str], list[str]]] = None
try:
    from scripts.repository import get_git_tracked_files as _imported_get_git_tracked_files  # type: ignore[attr-defined, unused-ignore]
    _get_git_tracked_files = _imported_get_git_tracked_files
except ImportError:
    pass

_calculate_repository_health: Optional[Callable[[int, int], Optional[float]]] = None
try:
    from scripts.report import calculate_repository_health as _imported_calculate_repository_health  # type: ignore[attr-defined, unused-ignore]
    _calculate_repository_health = _imported_calculate_repository_health
except ImportError:
    pass


# Global tracking for active AI review subprocess
_active_proc: Optional[subprocess.Popen] = None


# --- Helper Functions ---


def _read_state() -> dict[str, Any]:
    """
    Reads the current application state from the state file.

    Handles file not found or JSON decode errors gracefully, returning an empty
    dictionary in case of issues.
    """
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            _append_log(f"Warning: Could not decode {STATE_FILE}, starting with empty state.")
            return {}
        except Exception as e:
            _append_log(f"Warning: An unexpected error occurred reading {STATE_FILE}: {e}, starting with empty state.")
            return {}
    return {}


def _write_state(state: dict[str, Any]) -> None:
    """
    Writes the current application state to the state file.

    Ensures parent directories exist. `datetime` objects are converted to strings
    if present in the state dictionary.
    """
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, default=str), encoding="utf-8")


def _append_log(line: str) -> None:
    """
    Appends a line to the review log file.

    Ensures parent directories exist. Each line is stripped of trailing whitespace
    and followed by a newline.
    """
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(line.rstrip() + "\n")


def _start_review_in_thread(mode: str) -> None:
    """
    Starts an AI review process in a background thread as a separate Python subprocess.

    This function sets up the initial state for the review, launches the `scripts.ai_review`
    module in a new process, streams its output to the log file, and updates the
    application state upon completion.
    """

    def _run() -> None:
        """The actual review execution logic, run in a separate thread."""
        global _active_proc
        state: dict[str, Any] = {
            "running": True,
            "mode": mode,
            "start_time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "pid": None,
            "exit_code": None,
            "cancelled": False,
            "progress": {
                "completed": 0,
                "total": 0,
                "percentage": 0,
            },
        }
        _write_state(state)

        try:
            _append_log(f"Starting subprocess review (mode={mode})")
            proc = subprocess.Popen(
                [sys.executable, "-u", "-m", "scripts.ai_review", mode],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
            )
            _active_proc = proc
            state["pid"] = proc.pid
            _write_state(state)

            assert proc.stdout is not None
            for line in proc.stdout:
                _append_log(line)
            proc.wait()
            state["exit_code"] = proc.returncode
            _append_log(f"Subprocess exited with {proc.returncode}")
        except Exception as e:
            _append_log(f"Subprocess encountered exception: {e}")
        finally:
            _active_proc = None
            # Read current state to preserve any concurrent modifications (like cancellation)
            curr_state = _read_state()
            curr_state["running"] = False
            if curr_state.get("cancelled"):
                curr_state["exit_code"] = -1
            elif "exit_code" not in curr_state or curr_state["exit_code"] is None:
                curr_state["exit_code"] = proc.returncode if 'proc' in locals() else -1
            curr_state["end_time"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            _write_state(curr_state)

    t = threading.Thread(target=_run, daemon=True)
    t.start()


def _get_git_branch_name() -> str:
    """Retrieves the current Git branch name."""
    try:
        return (
            subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )
            .stdout.strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
        _append_log(f"Warning: Could not determine git branch: {e}")
        return "unknown"


def _get_last_git_commit_datetime() -> Optional[datetime]:
    """Retrieves the timestamp of the last Git commit."""
    try:
        res = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=iso-strict"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8"
        )
        date_str = res.stdout.strip()
        if date_str:
            return datetime.fromisoformat(date_str)
    except Exception as e:
        _append_log(f"Warning: Could not determine last git commit date: {e}")
    return None


def _get_fs_last_modified_datetime() -> Optional[datetime]:
    """
    Retrieves the most recent modification timestamp of any non-excluded file
    in the current working directory.
    """
    try:
        root = Path.cwd()
        latest_time = 0.0
        excluded_parts = {".git", "reports", "__pycache__", "lib", "web", ".venv", "venv", "node_modules"}
        for p in root.rglob("*"):
            if p.is_file() and not any(part in excluded_parts for part in p.parts):
                mtime = p.stat().st_mtime
                if mtime > latest_time:
                    latest_time = mtime
        if latest_time > 0:
            return datetime.fromtimestamp(latest_time, tz=timezone.utc)
    except Exception as e:
        _append_log(f"Warning: Failed to get filesystem last modified date: {e}")
    return None


def _format_datetime_for_display(dt_obj: Optional[datetime], fallback_text: str = "Recently") -> str:
    """Formats a datetime object into a human-readable string, or returns fallback_text."""
    if dt_obj:
        return dt_obj.strftime("%b %d, %Y at %I:%M %p (UTC)")
    return fallback_text


def _get_repo_files_count() -> int:
    """
    Counts the number of tracked files in the repository.
    Prioritizes `scripts.repository.get_git_tracked_files`, falls back to `git ls-files`,
    and finally to `Path.rglob` with exclusions.
    """
    if _get_git_tracked_files:
        try:
            return len(_get_git_tracked_files("all"))
        except Exception as e:
            _append_log(f"Warning: Failed to get git tracked files from script: {e}")

    try:
        out = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=True, encoding="utf-8"
        ).stdout
        return len([l for l in out.splitlines() if l.strip()])
    except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
        _append_log(f"Warning: Failed to get git tracked files via 'git ls-files': {e}")

    # Fallback to file system glob
    try:
        root = Path.cwd()
        excluded_parts = {".git", ".github", "lib", "node_modules", "__pycache__", ".venv", "venv", ".gradle", ".cache"}
        count = 0
        for p in root.rglob("*"):
            if p.is_file() and not any(part in excluded_parts or part.startswith(".") for part in p.parts):
                count += 1
        return count
    except Exception as e:
        _append_log(f"Warning: Failed to get git tracked files via rglob fallback: {e}")
        return 0


def _get_projects_count() -> int:
    """Dynamically counts custom coding/experiment folders in the repository root."""
    try:
        excluded = {
            ".git", ".github", "app", "web", "scripts", "docs", "reports",
            "prompts", "Jupyter_checkpoints", "__pycache__", "lib", "node_modules", ".venv", "venv"
        }
        root = Path.cwd()
        count = 0
        for item in root.iterdir():
            if item.is_dir() and item.name not in excluded and not item.name.startswith("."):
                count += 1
        return count if count > 0 else 5  # Fallback to 5 if no projects found
    except Exception as e:
        _append_log(f"Warning: Failed to count projects: {e}")
        return 5


def _parse_latest_report_stats() -> tuple[int, int]:
    """
    Parses the latest AI review report for "Files Changed" and "Files Failed" metrics.
    Returns (changed_files, failed_files).
    """
    changed = 0
    failed = 0
    if REPORTS_DIR.exists():
        latest_report = next(REPORTS_DIR.glob("*.md"), None)
        if latest_report:
            try:
                text = latest_report.read_text(encoding="utf-8")
                for line in text.splitlines():
                    if line.startswith("Files Changed"):
                        try:
                            changed = int(line.split(":", 1)[1].strip())
                        except ValueError:
                            pass
                    if line.startswith("Files Failed"):
                        try:
                            failed = int(line.split(":", 1)[1].strip())
                        except ValueError:
                            pass
            except Exception as e:
                _append_log(f"Warning: Failed to parse latest report {latest_report.name}: {e}")
    return changed, failed


def _is_valid_file_path(candidate: str) -> bool:
    """
    Validates if candidate string is a real file path and not a Markdown label like 'What Changed' or 'Why Changed'.
    """
    if not candidate:
        return False
    clean = candidate.strip().strip(":").strip("`").strip("*").strip()
    clean_lower = clean.lower()
    if clean_lower in ("what changed", "why changed", "what", "why", "none", "n/a", "no changes", "null", "details", "summary", "reason"):
        return False
    if clean_lower.startswith("what ") or clean_lower.startswith("why ") or clean_lower.endswith(":"):
        return False
    return True


def _format_health_value(health_input: Any) -> str:
    """
    Consistently formats repository health value to an integer percentage string (e.g. '100%').
    Prevents multiplying already percentage values (e.g. 100 -> 10000%).
    """
    if health_input is None:
        return "100%"
    if isinstance(health_input, str):
        h_str = health_input.strip()
        if not h_str or h_str.lower() in ("pending", "n/a", "none", "null"):
            calc = _get_calculated_repo_health()
            return _format_health_value(calc)
        if h_str.endswith("%"):
            try:
                num = float(h_str.rstrip("%"))
                if num > 100:
                    num = 100.0
                return f"{num:.0f}%"
            except ValueError:
                return h_str
        try:
            num = float(h_str)
            return _format_health_value(num)
        except ValueError:
            return h_str
    try:
        val = float(health_input)
        if val <= 1.0 and val > 0:
            val = val * 100.0
        val = min(100.0, max(0.0, val))
        return f"{val:.0f}%"
    except (ValueError, TypeError):
        return "100%"


def _get_calculated_repo_health() -> Optional[float]:
    """
    Calculates repository health using the imported script function, if available.
    Relies on metrics parsed from the latest report.
    """
    if _calculate_repository_health:
        changed, failed = _parse_latest_report_stats()
        try:
            return _calculate_repository_health(changed, failed)
        except Exception as e:
            _append_log(f"Warning: Failed to calculate repository health from script: {e}")
    return None


def _get_detailed_file_changes() -> list[dict[str, str]]:
    """
    Retrieves detailed file change explanations (Which, What, Why) from state cache or Markdown report.
    """
    stats_file = Path.cwd() / ".cache" / "dashboard_stats.json"
    if stats_file.exists():
        try:
            data = json.loads(stats_file.read_text(encoding="utf-8"))
            if "recent_file_changes" in data and isinstance(data["recent_file_changes"], list):
                if data["recent_file_changes"]:
                    return data["recent_file_changes"]
        except Exception:
            pass

    report_path = AI_REPORT if AI_REPORT.exists() else None
    if not report_path and REPORTS_DIR.exists():
        reports = sorted(REPORTS_DIR.glob("*_review.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if reports:
            report_path = reports[0]

    if report_path and report_path.exists():
        try:
            content = report_path.read_text(encoding="utf-8")
            if "## Detailed File Changes" in content:
                section = content.split("## Detailed File Changes", 1)[1]
                if "## " in section:
                    section = section.split("## ", 1)[0]
                changes = []
                current = None
                for line in section.splitlines():
                    ls = line.strip()
                    if ls.startswith("- **`") and "`**" in ls:
                        if current:
                            changes.append(current)
                        fname = ls.split("- **`")[1].split("`**")[0]
                        current = {"file": fname, "what": "N/A", "why": "N/A"}
                    elif current and "**What Changed**:" in ls:
                        current["what"] = ls.split("**What Changed**:", 1)[1].strip()
                    elif current and "**Why Changed**:" in ls:
                        current["why"] = ls.split("**Why Changed**:", 1)[1].strip()
                if current:
                    changes.append(current)
                if changes:
                    return changes
        except Exception:
            pass

    return []


def _get_review_history(limit: int = 5) -> list[dict[str, Any]]:
    """
    Retrieves the list of up to `limit` most recent review execution timestamps and health scores.
    Checks report files in REPORTS_DIR, falling back to AI_REPORT.md or application state.
    """
    history: list[dict[str, Any]] = []

    # 1. Parse report files in REPORTS_DIR
    if REPORTS_DIR.exists():
        report_files = sorted(REPORTS_DIR.glob("*_review.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not report_files:
            report_files = sorted(REPORTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)

        for report in report_files:
            if len(history) >= limit:
                break
            try:
                content = report.read_text(encoding="utf-8")
                date_val = "N/A"
                time_val = ""
                health_val = ""
                for line in content.splitlines():
                    ls = line.strip()
                    if ls.startswith("- Date:"):
                        date_val = ls.split(":", 1)[1].strip()
                    elif ls.startswith("- Time:"):
                        time_val = ls.split(":", 1)[1].strip()
                    elif ls.startswith("Overall Score") or ls.startswith("- Overall Score"):
                        health_val = ls.split(":", 1)[1].strip()

                if date_val != "N/A":
                    ts_str = f"{date_val} {time_val}".strip()
                    try:
                        dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                        display_ts = dt.strftime("%b %d, %Y %I:%M:%S %p")
                    except Exception:
                        display_ts = ts_str
                else:
                    mtime = report.stat().st_mtime
                    dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
                    display_ts = dt.strftime("%b %d, %Y %I:%M:%S %p")

                if not health_val or health_val.lower() in ("pending", "n/a"):
                    calc = _get_calculated_repo_health()
                    health_val = _format_health_value(calc)
                else:
                    health_val = _format_health_value(health_val)

                history.append({
                    "timestamp": display_ts,
                    "health": health_val,
                    "report_name": report.name
                })
            except Exception:
                pass

    # 2. If no reports found in REPORTS_DIR, check AI_REPORT.md for recent reports list
    if len(history) < limit and AI_REPORT.exists():
        try:
            content = AI_REPORT.read_text(encoding="utf-8")
            if "## Recent Reports" in content:
                section = content.split("## Recent Reports", 1)[1]
                if "## " in section:
                    section = section.split("## ", 1)[0]
                for line in section.splitlines():
                    if len(history) >= limit:
                        break
                    ls = line.strip()
                    if ls.startswith("- [") and "](reports/" in ls:
                        r_file = ls.split("](reports/", 1)[1].rstrip(")")
                        try:
                            parts = r_file.replace("_review.md", "").replace(".md", "").split("_")
                            if len(parts) >= 2:
                                dt_str = f"{parts[0]} {parts[1].replace('-', ':')}"
                                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                                display_ts = dt.strftime("%b %d, %Y %I:%M:%S %p")
                            else:
                                display_ts = r_file
                        except Exception:
                            display_ts = r_file
                        calc = _get_calculated_repo_health()
                        health_str = _format_health_value(calc)
                        
                        if not any(h["report_name"] == r_file for h in history):
                            history.append({
                                "timestamp": display_ts,
                                "health": health_str,
                                "report_name": r_file
                            })
        except Exception:
            pass

    # 3. Fallback to state's last review execution timestamp if history is still empty
    if not history:
        state = _read_state()
        last_review_dt = None
        if state.get("end_time"):
            try:
                last_review_dt = datetime.fromisoformat(state["end_time"].replace("Z", "+00:00"))
            except Exception:
                pass
        if last_review_dt:
            calc = _get_calculated_repo_health()
            health_str = _format_health_value(calc)
            history.append({
                "timestamp": last_review_dt.strftime("%b %d, %Y %I:%M:%S %p"),
                "health": health_str,
                "report_name": "Latest Execution"
            })

    return history[:limit]


def _get_repo_stats_for_dashboard() -> dict[str, Any]:

    """
    Aggregates all repository-related statistics needed for the dashboard.
    This includes branch, last updated, file counts, review status, and health.
    """
    state = _read_state()

    # Determine last review time
    last_review_dt: Optional[datetime] = None
    if state.get("end_time"):
        try:
            last_review_dt = datetime.fromisoformat(state["end_time"].replace("Z", "+00:00"))
        except Exception:
            pass # Malformed date string in state
    else:
        # Fallback to modification time of the latest report file
        if REPORTS_DIR.exists():
            files = sorted(REPORTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
            if files:
                last_review_dt = datetime.fromtimestamp(files[0].stat().st_mtime, tz=timezone.utc)

    # Determine last updated time (git commit or file system)
    last_updated_dt = _get_last_git_commit_datetime()
    if last_updated_dt is None:
        last_updated_dt = _get_fs_last_modified_datetime()

    return {
        "repo_name": Path.cwd().name,
        "branch": _get_git_branch_name(),
        "last_updated": _format_datetime_for_display(last_updated_dt, fallback_text="Recently"),
        "files_discovered": _get_repo_files_count(),
        "total_projects": _get_projects_count(),
        "last_review": _format_datetime_for_display(last_review_dt, fallback_text="Never"),
        "repo_health": _get_calculated_repo_health(),
        "state": state,
        "available_models": AVAILABLE_MODELS,
        "file_changes": _get_detailed_file_changes(),
        "review_history": _get_review_history(5),
    }



def _get_tracked_files_list() -> list[str]:
    """
    Gets the list of all tracked or discovered files in the repository.
    Prioritizes `scripts.repository.get_git_tracked_files`, falls back to `git ls-files`,
    and finally to `Path.rglob` with exclusions.
    """
    if _get_git_tracked_files:
        try:
            paths = _get_git_tracked_files("all")
            return [str(p) for p in paths]
        except Exception as e:
            _append_log(f"Warning: Failed to get git tracked files list from script: {e}")

    try:
        out = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=True, encoding="utf-8"
        ).stdout
        return [l.strip() for l in out.splitlines() if l.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
        _append_log(f"Warning: Failed to get git tracked files via 'git ls-files': {e}")

    # Fallback to file system glob
    try:
        root = Path.cwd()
        excluded_parts = {".git", ".github", "lib", "node_modules", "__pycache__", ".venv", "venv", ".gradle", ".cache"}
        files = []
        for p in root.rglob("*"):
            if p.is_file() and not any(part in excluded_parts or part.startswith(".") for part in p.parts):
                try:
                    files.append(str(p.relative_to(root)))
                except Exception:
                    pass  # File not relative to root or other path issue
        return sorted(files)
    except Exception as e:
        _append_log(f"Warning: Failed to get git tracked files via rglob fallback: {e}")
        return []


# --- Flask Routes ---


@app.route("/switch-model", methods=["POST"])
def switch_model() -> Response:
    """
    API endpoint to switch the currently selected AI model.
    Expects a POST request with a 'model' parameter in the JSON body.
    """
    data: dict[str, Any] = request.get_json() or {}
    model: Optional[str] = data.get("model")

    if not model or model not in AVAILABLE_MODELS:
        return jsonify({"success": False, "reason": "invalid_model"}), 400

    state = _read_state()
    state["model"] = model
    _write_state(state)

    return jsonify({"success": True})


@app.route("/")
def index() -> str:
    """
    Renders the main dashboard page, displaying repository information,
    last review status, and links to reports.
    """
    context = _get_repo_stats_for_dashboard()
    return render_template("index.html", active_tab="home", **context)


@app.route("/repo-stats")
def repo_stats() -> Response:
    """
    Returns repository statistics as JSON.
    This includes branch, last updated, file counts, review status, and health.
    """
    stats = _get_repo_stats_for_dashboard()
    return jsonify({
        "repo_name": stats["repo_name"],
        "branch": stats["branch"],
        "last_updated": stats["last_updated"],
        "files_discovered": stats["files_discovered"],
        "total_projects": stats["total_projects"],
        "last_review": stats["last_review"],
        "repo_health": stats["repo_health"],
        "current_model": stats["state"].get("model"),
        "review_history": stats["review_history"],
    })


@app.route("/api/files")
def api_files() -> Response:
    """Returns the list of git-tracked or repository files."""
    return jsonify({"files": _get_tracked_files_list()})


@app.route("/api/file-content")
def api_file_content() -> Response | tuple[Response, int]:
    """
    Returns the text content and metadata of a specified file.
    Performs path sanitization to prevent directory traversal.
    """
    file_path_str: Optional[str] = request.args.get("path")
    if not file_path_str:
        return jsonify({"success": False, "error": "No file path provided"}), 400

    root = Path.cwd().resolve()
    target_path = (root / file_path_str).resolve()

    if not target_path.exists():
        return jsonify({"success": False, "error": "File does not exist"}), 404

    if not target_path.is_file():
        return jsonify({"success": False, "error": "Not a file"}), 400

    # Security check: Ensure the requested path is within the current working directory.
    if not str(target_path).startswith(str(root)):
        return jsonify({"success": False, "error": "Access denied"}), 403

    try:
        content = target_path.read_text(encoding="utf-8", errors="replace")
        mtime = target_path.stat().st_mtime
        size = target_path.stat().st_size
        dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            "success": True,
            "path": file_path_str,
            "content": content,
            "size": size,
            "last_modified": formatted_time
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to read file: {str(e)}"}), 500


@app.route("/run-review", methods=["POST"])
def run_review() -> Response | tuple[Response, int]:
    """
    Endpoint to trigger an AI review.
    Expects a POST request with an optional 'mode' parameter in JSON body or query args.
    Returns status JSON indicating if the review started or why it didn't.
    """
    data: dict[str, Any] = request.get_json() or {}
    mode: str = data.get("mode") or request.args.get("mode") or "modified"

    state = _read_state()
    if state.get("running"):
        return jsonify({"started": False, "reason": "already_running"}), 409

    # Clear the log file for the new run so the live view is fresh and relevant.
    if LOG_FILE.exists():
        try:
            LOG_FILE.write_text("", encoding="utf-8")
        except Exception as e:
            _append_log(f"Warning: Could not truncate log file: {e}")

    _start_review_in_thread(mode)
    return jsonify({"started": True, "mode": mode})


@app.route("/cancel-review", methods=["POST"])
def cancel_review() -> Response:
    """
    Endpoint to cancel a currently running review subprocess.
    """
    global _active_proc
    state = _read_state()

    if not state.get("running"):
        return jsonify({"success": False, "error": "No review is currently running"}), 400

    cancelled = False

    # Try terminating the subprocess object directly
    if _active_proc is not None:
        try:
            _active_proc.terminate()
            try:
                _active_proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                _active_proc.kill()
            cancelled = True
        except Exception as e:
            _append_log(f"Error terminating via object reference: {e}")

    # Fallback to process group or PID killing
    if not cancelled and state.get("pid"):
        try:
            import os
            import signal
            pid = int(state["pid"])
            os.kill(pid, signal.SIGTERM)
            cancelled = True
        except Exception as e:
            _append_log(f"Error terminating PID {state.get('pid')}: {e}")

    if cancelled:
        state["running"] = False
        state["cancelled"] = True
        state["exit_code"] = -1
        state["end_time"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        _write_state(state)
        _append_log("AI review was manually cancelled by the user.")
        _active_proc = None
        return jsonify({"success": True})

    # Fallback: force update status to Stopped
    state["running"] = False
    state["cancelled"] = True
    _write_state(state)
    return jsonify({"success": True, "note": "Force updated state to stopped"})


@app.route("/status")
def status() -> Response:
    """
    Returns the current application state and the tail of the review log as JSON.
    The log tail is limited to the last 300 lines for performance.
    """
    state = _read_state()
    tail: list[str] = []
    if LOG_FILE.exists():
        try:
            with LOG_FILE.open("r", encoding="utf-8") as fh:
                lines = fh.read().splitlines()
                tail = lines[-300:]
        except Exception as e:
            _append_log(f"Error reading log file: {e}")
            tail = ["<could not read log due to an error>"]
    return jsonify({
        "state": state,
        "log": tail,
        "file_changes": _get_detailed_file_changes(),
        "review_history": _get_review_history(5)
    })



# --- Report Parsing & Diff Helpers ---


def _extract_changed_files_from_markdown(content: str) -> list[str]:
    """
    Extracts changed file names from Markdown content (e.g. ## Modified Files, ## Detailed File Changes, ## Recent Modified Files).
    """
    files: list[str] = []
    lines = content.splitlines()
    in_target_section = False

    for line in lines:
        s = line.strip()
        if s.startswith("## "):
            header = s[3:].strip().lower()
            if any(k in header for k in ["modified files", "detailed file changes", "recent modified files", "changed files"]):
                in_target_section = True
            else:
                in_target_section = False
            continue

        if in_target_section:
            if s.startswith("- **`") and "`**" in s:
                f = s.split("- **`", 1)[1].split("`**", 1)[0].strip()
                if _is_valid_file_path(f) and f not in files:
                    files.append(f)
            elif s.startswith("- **") and "**" in s:
                f = s.split("- **", 1)[1].split("**", 1)[0].strip()
                if _is_valid_file_path(f) and f not in files:
                    files.append(f)
            elif s.startswith("- `") and "`" in s:
                f = s.split("- `", 1)[1].split("`", 1)[0].strip()
                if _is_valid_file_path(f) and f not in files:
                    files.append(f)
            elif s.startswith("- "):
                f = s[2:].strip()
                if _is_valid_file_path(f) and f not in files:
                    files.append(f)

    return files


def _extract_detailed_changes_map(content: str) -> dict[str, dict[str, str]]:
    """
    Extracts a mapping of file_path -> {"what": ..., "why": ...} from ## Detailed File Changes in report content.
    """
    result: dict[str, dict[str, str]] = {}
    lines = content.splitlines()
    in_section = False
    current_file = None

    for line in lines:
        s = line.strip()
        if s.startswith("## "):
            in_section = ("detailed file changes" in s.lower())
            current_file = None
            continue

        if in_section:
            if s.startswith("- **`") and "`**" in s:
                cand = s.split("- **`", 1)[1].split("`**", 1)[0].strip()
                if _is_valid_file_path(cand):
                    current_file = cand
                    result[current_file] = {"what": "Code modifications applied", "why": "Improve quality and maintainability"}
            elif s.startswith("- **") and "**" in s:
                cand = s.split("- **", 1)[1].split("**", 1)[0].strip()
                if _is_valid_file_path(cand):
                    current_file = cand
                    result[current_file] = {"what": "Code modifications applied", "why": "Improve quality and maintainability"}
            elif current_file and "**What Changed**:" in s:
                result[current_file]["what"] = s.split("**What Changed**:", 1)[1].strip()
            elif current_file and "**Why Changed**:" in s:
                result[current_file]["why"] = s.split("**Why Changed**:", 1)[1].strip()

    return result


def _extract_embedded_diffs(content: str) -> dict[str, str]:
    """
    Parses embedded ```diff blocks from Markdown content under ## Code Diffs or ### `filename`.
    """
    embedded: dict[str, str] = {}
    if "## Code Diffs" not in content and "## File Diffs" not in content and "```diff" not in content:
        return embedded

    sections = re.split(r'\n###\s+`?([^`\n]+)`?\n', content)
    for i in range(1, len(sections), 2):
        fname = sections[i].strip()
        sec_text = sections[i+1] if i+1 < len(sections) else ""
        if "```diff" in sec_text:
            diff_block = sec_text.split("```diff", 1)[1].split("```", 1)[0].strip()
            embedded[fname] = diff_block
        elif "```" in sec_text:
            diff_block = sec_text.split("```", 1)[1].split("```", 1)[0].strip()
            embedded[fname] = diff_block

    return embedded


def _get_git_diff_for_file(filepath: str) -> str:
    """
    Fetches raw git diff for a filepath using git diff or git log commands.
    """
    cmds = [
        ["git", "diff", "HEAD~1", "HEAD", "--", filepath],
        ["git", "diff", "HEAD", "--", filepath],
        ["git", "log", "-p", "-1", "--", filepath],
        ["git", "diff", "--", filepath]
    ]
    for cmd in cmds:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.stdout and ("diff --git" in res.stdout or "@@ " in res.stdout):
                return res.stdout.strip()
        except Exception:
            pass
    return ""


def _format_diff_html(diff_text: str) -> str:
    """
    Formats a raw diff string into syntax-highlighted HTML with color-coded additions/deletions.
    """
    if not diff_text:
        return ""
    lines = diff_text.splitlines()
    html_lines = []
    for line in lines:
        escaped = html.escape(line)
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@") or line.startswith("diff --git") or line.startswith("index "):
            html_lines.append(f'<div class="diff-line diff-header">{escaped}</div>')
        elif line.startswith("+"):
            html_lines.append(f'<div class="diff-line diff-add">{escaped}</div>')
        elif line.startswith("-"):
            html_lines.append(f'<div class="diff-line diff-del">{escaped}</div>')
        else:
            html_lines.append(f'<div class="diff-line diff-context">{escaped}</div>')

    return f'<div class="diff-code-wrapper"><pre class="diff-code">{"".join(html_lines)}</pre></div>'


def _get_report_file_diffs(content: str, changed_files: list[str]) -> list[dict[str, Any]]:
    """
    Builds structured file diff details for a report, combining detailed change reasons and code diffs.
    """
    details_map = _extract_detailed_changes_map(content)
    embedded_diffs = _extract_embedded_diffs(content)

    results: list[dict[str, Any]] = []
    for filepath in changed_files:
        what = details_map.get(filepath, {}).get("what", "Code modifications applied")
        why = details_map.get(filepath, {}).get("why", "Improve quality and maintainability")

        raw_diff = embedded_diffs.get(filepath, "")
        if not raw_diff:
            raw_diff = _get_git_diff_for_file(filepath)

        diff_html = _format_diff_html(raw_diff) if raw_diff else ""

        results.append({
            "file": filepath,
            "what": what,
            "why": why,
            "raw_diff": raw_diff,
            "diff_html": diff_html
        })
    return results


@app.route("/reports")
def list_reports() -> str:
    """
    Renders a page listing all available AI review reports with their changed files list.
    Reports are sorted by modification time, newest first.
    """
    if not REPORTS_DIR.exists():
        return render_template("reports.html", reports=[], active_tab="reports")

    entries: list[dict[str, Any]] = []
    for p in sorted(REPORTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            content = p.read_text(encoding="utf-8")
            changed_files = _extract_changed_files_from_markdown(content)
        except Exception:
            changed_files = []

        entries.append(
            {
                "name": p.name,
                "path": str(p),
                "date": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "changed_files": changed_files,
                "changed_count": len(changed_files)
            }
        )
    return render_template("reports.html", reports=entries, active_tab="reports")


@app.route("/reports/view/<path:filename>")
def view_report(filename: str) -> str:
    """
    Renders a specific AI review report from the 'reports' directory,
    including the changed files list and file-by-file code diff view.
    """
    p = REPORTS_DIR / filename
    if not p.exists() or not p.is_file():
        abort(404)
    text = p.read_text(encoding="utf-8")

    changed_files = _extract_changed_files_from_markdown(text)
    file_diffs = _get_report_file_diffs(text, changed_files)

    html_content: str
    try:
        import markdown
        html_content = markdown.markdown(text, extensions=["fenced_code", "tables"])  # type: ignore[attr-defined]
    except ImportError:
        _append_log("Warning: 'markdown' library not found, rendering reports as plain text.")
        html_content = f"<pre>{text}</pre>"
    except Exception as e:
        _append_log(f"Error rendering markdown for {filename}: {e}")
        html_content = f"<pre>{text}</pre>"

    return render_template(
        "report_view.html",
        content=html_content,
        filename=filename,
        changed_files=changed_files,
        file_diffs=file_diffs,
        active_tab="reports"
    )


@app.route("/reports/<path:filename>")
def serve_report_file_fallback(filename: str) -> Response:
    """
    Catch requests originating from relative dashboard links (e.g. ../reports/...)
    and redirect them to the dynamic markdown viewer.
    """
    from flask import redirect, url_for
    cleaned = filename
    if cleaned.startswith("reports/"):
        cleaned = cleaned[len("reports/"):]
    return redirect(url_for('view_report', filename=cleaned))


@app.route("/ai_report")
def ai_report() -> str:
    """
    Renders the main AI_REPORT.md file with changed files list and code diffs.
    """
    if not AI_REPORT.exists():
        return render_template("ai_report.html", active_tab="ai_report")
    text = AI_REPORT.read_text(encoding="utf-8")

    changed_files = _extract_changed_files_from_markdown(text)
    file_diffs = _get_report_file_diffs(text, changed_files)

    html_content: str
    try:
        import markdown
        html_content = markdown.markdown(text, extensions=["fenced_code", "tables"])  # type: ignore[attr-defined]
    except ImportError:
        _append_log("Warning: 'markdown' library not found, rendering AI report as plain text.")
        html_content = f"<pre>{text}</pre>"
    except Exception as e:
        _append_log(f"Error rendering markdown for {AI_REPORT.name}: {e}")
        html_content = f"<pre>{text}</pre>"

    return render_template(
        "report_view.html",
        content=html_content,
        filename=AI_REPORT.name,
        changed_files=changed_files,
        file_diffs=file_diffs,
        active_tab="ai_report"
    )


def _prepare_dashboard_html(file_path: Path) -> str:
    content = file_path.read_text(encoding="utf-8")
    body_match = re.search(r"<body[^>]*>(.*?)</body>", content, re.DOTALL | re.IGNORECASE)
    body_html = body_match.group(1) if body_match else content

    head_match = re.search(r"<head[^>]*>(.*?)</head>", content, re.DOTALL | re.IGNORECASE)
    head_html = ""
    if head_match:
        tags = re.findall(r"(<script[^>]*>.*?</script>|<style[^>]*>.*?</style>)", head_match.group(1), re.DOTALL | re.IGNORECASE)
        head_html = "\n".join(tags)
    return head_html + "\n" + body_html


@app.route("/dashboard")
def dashboard() -> Response | str:
    """
    Serves the visual repository dashboard inside the template layout with top navigation.
    """
    docs_dashboard_path = Path.cwd() / "docs" / "dashboard.html"
    reports_dashboard_path = Path.cwd() / "reports" / "dashboard.html"

    if docs_dashboard_path.exists():
        content = _prepare_dashboard_html(docs_dashboard_path)
        return render_template("dashboard.html", dashboard_exists=True, dashboard_content=content, active_tab="dashboard")
    elif reports_dashboard_path.exists():
        content = _prepare_dashboard_html(reports_dashboard_path)
        return render_template("dashboard.html", dashboard_exists=True, dashboard_content=content, active_tab="dashboard")
    return render_template("dashboard.html", dashboard_exists=False, active_tab="dashboard")


if __name__ == "__main__":
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        _write_state({"running": False})
    if not LOG_FILE.exists():
        LOG_FILE.write_text("", encoding="utf-8")
    port_env = os.environ.get("PORT")
    if not port_env or port_env in ("8080", "8000"):
        port = 3000
    else:
        try:
            port = int(port_env)
        except ValueError:
            port = 3000
    app.run(host="0.0.0.0", port=port)