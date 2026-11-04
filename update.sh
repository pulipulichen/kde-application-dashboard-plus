#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_dir"
[[ $(git branch --show-current) == main ]] || { echo 'Switch to main before updating.' >&2; exit 1; }
[[ -z $(git status --porcelain) ]] || { echo 'Uncommitted changes found. Commit or stash them before updating.' >&2; exit 1; }
git pull --ff-only origin main
exec "$project_dir/install.sh"
