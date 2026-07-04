"""
Global configuration for the Daily AI Review project.
"""

# ==========================
# Gemini Configuration
# ==========================

MODEL = "gemini-2.5-flash"

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