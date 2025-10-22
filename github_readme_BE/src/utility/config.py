# Safety limits to keep prompts small (character-based, coarse control)
MAX_FILES_TO_SUMMARIZE = 120           # cap number of files summarized
MAX_CHARS_PER_FILE_SNIPPET = 4000      # truncate each file's content

# Configure which file extensions count as "programming language files"
CODE_EXTS = {
    ".py", ".ipynb", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".kt", ".kts", ".scala",
    ".c", ".cc", ".cpp", ".h", ".hpp",
    ".cs", ".go", ".rs", ".rb", ".php",
    ".swift", ".m", ".mm",
    ".pl", ".sh", ".bash", ".zsh", ".ps1", ".bat",
    ".r", ".jl", ".sql",
    ".html", ".sass", ".xml", ".yml", ".yaml", ".ini", ".gradle"
}

# Common directories to skip (tweak as needed)
DEFAULT_EXCLUDE_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".idea", ".vscode",
    "node_modules", "venv", ".venv", "env", ".mypy_cache",
    "build", "dist", "target", ".next", ".nuxt", ".pytest_cache", "out", ".toml", ".txt"
}

PROJECT_TABLE = "projects"
PROJECT_FILES_TABLE = "project_files"