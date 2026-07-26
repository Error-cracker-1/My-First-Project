"""
Global configuration for the Daily AI Review project.
"""

# ==========================
# Gemini Configuration
# ==========================

MODEL = "gemini-2.5-flash"

STATE_FILE_PATH = "web/.web_review_state.json"

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

MAX_RETRIES = 5

INITIAL_DELAY = 25


# ==========================
# Git Configuration
# ==========================

TARGET_BRANCH = "feature-1"


# ==========================
# Review Configuration
# ==========================

REVIEW_DELAY = 2

SKIP_SELF_REVIEW = True


SELF_REVIEW_PATHS = {
    "scripts",
    "prompts",
    ".github",
}

# ==========================
# Supported File Types
# ==========================

SUPPORTED_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".html",
    ".css",
    ".js",
    ".json",
    ".yml",
    ".yaml",
    ".ps1",
}


# ==========================
# Ignored Directories
# ==========================

EXCLUDED_DIRECTORIES = {
    ".git",
    ".github",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".vscode",
    "lib",
    "Game Pong",
    "Jupyter",
    "Web 1",
    "Powershell",
    "Python",
    ".gradle",
    ".cache",
}

# ==========================================================
# Backup Configuration
# ==========================================================

# Extension used for temporary backup files.
BACKUP_EXTENSION = ".bak"


# ==========================
# Ignored Files
# ==========================

EXCLUDED_FILES = {
    "AI_CHANGELOG.md",
}