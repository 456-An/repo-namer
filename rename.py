import sys
import os
import argparse
import subprocess
from cleaner import clean_name
from pathlib import Path

def rename_recursive(folder_path: Path, apply=False, ignore_dirs=None, use_git=False, style='kebab'):
    if ignore_dirs is None:
        ignore_dirs = {'.git', 'node_modules', '.venv'}
    rename_log = []

    for root, dirs, files in os.walk(folder_path, topdown=False):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        # Skip files in ignored directories
        current_path = Path(root)
        if any(ignored in current_path.parts for ignored in ignore_dirs):
            continue
            
        # Rename files
        for name in files:
            old_path = Path(root) / name
            new_name = clean_name(name, style)
            new_path = Path(root) / new_name
            if old_path != new_path:
                rename_log.append((old_path, new_path))
                if apply:
                    if use_git:
                        subprocess.run(['git', 'mv', str(old_path), str(new_path)], check=True)
                    else:
                        os.rename(old_path, new_path)

        # Rename directories
        for name in dirs:
            old_path = Path(root) / name
            new_name = clean_name(name, style)
            new_path = Path(root) / new_name
            if old_path != new_path:
                rename_log.append((old_path, new_path))
                if apply:
                    if use_git:
                        subprocess.run(['git', 'mv', str(old_path), str(new_path)], check=True)
                    else:
                        os.rename(old_path, new_path)

    return rename_log

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean and normalize folder/file names.")
    parser.add_argument("folder", help="Path to the folder you want to clean.")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run).")
    parser.add_argument("--ignore", help="Comma-separated list of directories to ignore (default: .git,node_modules,.venv)")
    parser.add_argument("--report", help="Output report file (optional)")
    parser.add_argument("--git", action="store_true", help="Use git mv instead of os.rename (for git repositories)")
    parser.add_argument("--style", choices=['kebab', 'snake', 'lower-camel', 'upper-camel'], default='kebab', help="Naming style (default: kebab)")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"❌ Folder does not exist: {folder}")
        sys.exit(1)

    # Handle ignored directories
    ignore_dirs = None
    if args.ignore:
        ignore_dirs = set(args.ignore.split(','))
        print(f"📁 Ignored directories: {', '.join(ignore_dirs)}")

    changes = rename_recursive(folder, apply=args.apply, ignore_dirs=ignore_dirs, use_git=args.git, style=args.style)

    if not changes:
        print("✅ No files or folders need to be renamed.")
    else:
        print("📝 The following items will be renamed (old → new):")
        for old, new in changes:
            print(f"  {old} → {new}")

        # Output report
        if args.report:
            with open(args.report, "w", encoding="utf-8") as f:
                for old, new in changes:
                    f.write(f"{old} → {new}\n")
            print(f"\n📝 Report written to {args.report}")

        if args.apply:
            print("\n✅ All changes have been applied!")
        else:
            print("\n⚠️ No changes applied (use --apply to execute renaming)")
