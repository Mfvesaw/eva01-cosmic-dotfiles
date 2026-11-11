#!/usr/bin/env bash
set -euo pipefail
if ! command -v python3 >/dev/null 2>&1; then
    printf '%s\n' 'Python 3.12 or newer is required.' >&2
    exit 1
fi
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else "Python 3.12 or newer is required.")'
exec python3 "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/scripts/install.py" "$@"
