"""Global configuration for the Daily AI Review project."""

MODEL = "gemini-2.5-flash"
STATE_FILE_PATH = "web/.web_review_state.json"
AVAILABLE_MODELS = ["gemini-2.5-flash","gemini-2.5-pro","gemini-2.0-flash","gemini-2.0-flash-lite","gemini-2.0-pro-exp","gemini-2.0-flash-thinking-exp","gemini-1.5-pro","gemini-1.5-flash","gemini-1.5-flash-8b","gemini-1.0-pro"]
MAX_RETRIES = 5
INITIAL_DELAY = 25
TARGET_BRANCH = "AI-Chatbot"
REVIEW_DELAY = 2
SKIP_SELF_REVIEW = True
SELF_REVIEW_PATHS = {"scripts","prompts",".github"}
SUPPORTED_EXTENSIONS = {".py",".md",".txt",".html",".css",".js",".json",".yml",".yaml",".ps1"}
EXCLUDED_DIRECTORIES = {".git",".github","__pycache__",".venv","venv","node_modules",".mypy_cache",".pytest_cache",".vscode","lib","Game Pong","Jupyter","Web 1","Powershell","Python",".gradle",".cache"}
BACKUP_EXTENSION = ".bak"
EXCLUDED_FILES = {"AI_CHANGELOG.md"}
