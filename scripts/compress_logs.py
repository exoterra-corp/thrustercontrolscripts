#!/usr/bin/env python3
"""Compress unarchived subdirectories in the logs folder."""

import argparse
import sys
import zipfile
from pathlib import Path


def compress_folder(folder: Path, output: Path, dry_run: bool) -> bool:
    files = list(folder.rglob("*"))
    if dry_run:
        print(f"  [dry-run] would compress {folder.name} -> {output.name} ({len(files)} files)")
        return True

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for f in files:
            if f.is_file():
                zf.write(f, f.relative_to(folder.parent))

    return True


def main():
    parser = argparse.ArgumentParser(description="Compress unarchived log subdirectories.")
    parser.add_argument(
        "logs_dir",
        nargs="?",
        default=Path(__file__).parent.parent / "logs",
        type=Path,
        help="Path to the logs directory (default: ../logs relative to this script)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be compressed without doing anything",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete the original folder after successful compression",
    )
    args = parser.parse_args()

    logs_dir = args.logs_dir.resolve()
    if not logs_dir.is_dir():
        print(f"Error: logs directory not found: {logs_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning: {logs_dir}")

    compressed = 0
    skipped = 0

    for entry in sorted(logs_dir.iterdir()):
        if not entry.is_dir():
            skipped += 1
            continue

        output = entry.with_suffix(".zip")
        if output.exists():
            print(f"  skip {entry.name} (archive already exists)")
            skipped += 1
            continue

        print(f"  compress {entry.name} -> {output.name}")
        try:
            ok = compress_folder(entry, output, args.dry_run)
        except Exception as exc:
            print(f"  ERROR compressing {entry.name}: {exc}", file=sys.stderr)
            continue

        if ok and args.delete and not args.dry_run:
            import shutil
            shutil.rmtree(entry)
            print(f"    deleted {entry.name}")

        compressed += 1

    print(f"\nDone: {compressed} compressed, {skipped} skipped.")


if __name__ == "__main__":
    main()
