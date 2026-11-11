#!/usr/bin/env bash
set -euo pipefail
repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python3 "$repo_dir/scripts/snapshot.py"
python3 "$repo_dir/scripts/check-backup.py" --write-checksums
printf '%s\n' 'Review git diff, then commit and push to your private repository.'
