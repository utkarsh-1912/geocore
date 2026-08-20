
import os

AUTHOR_HEADER_PY = """# Author: Utkarsh Gupta
# License: GPL v2
"""

AUTHOR_HEADER_JS = """/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */
"""

TARGET_DIRS = [
    r"C:\Users\utkar\Downloads\Geocore\python-backend",
    r"C:\Users\utkar\Downloads\Geocore\electron-app\src"
]

IGNORE_DIRS = ["venv", "node_modules", ".git", "__pycache__", "dist", "build", "site-packages"]

def add_header(filepath, header):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "Author: Utkarsh Gupta" in content:
            print(f"Skipping {filepath} (Already present)")
            return

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(header + "\n" + content)
        print(f"Updated {filepath}")
    except Exception as e:
        print(f"Failed to update {filepath}: {e}")

def main():
    for root_dir in TARGET_DIRS:
        for root, dirs, files in os.walk(root_dir):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                filepath = os.path.join(root, file)
                if file.endswith(".py"):
                    add_header(filepath, AUTHOR_HEADER_PY)
                elif file.endswith(".js") or file.endswith(".jsx"):
                    add_header(filepath, AUTHOR_HEADER_JS)

if __name__ == "__main__":
    main()
