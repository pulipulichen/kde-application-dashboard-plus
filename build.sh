#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
for tool in cmake python3 msgfmt; do
    command -v "$tool" >/dev/null || { echo "Missing dependency: $tool. Run ./install-deps.sh" >&2; exit 1; }
done
cmake -S "$project_dir" -B "$project_dir/build" -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBUILD_TESTING=ON
cmake --build "$project_dir/build" --parallel "${BUILD_JOBS:-2}"
ctest --test-dir "$project_dir/build" --output-on-failure
python3 "$project_dir/tests/check-package.py"
mkdir -p "$project_dir/dist"
# Stage a fresh package so stale native binaries/translations cannot be included.
stage_dir="$(mktemp -d "$project_dir/dist/stage.XXXXXXXX")"
trap 'rm -rf -- "$stage_dir"' EXIT
cp -a "$project_dir/package/." "$stage_dir/"
cp "$project_dir/build/dashboardplusnative/libdashboardplusplugin.so" "$stage_dir/contents/ui/dashboardplusnative/"
for language in zh_TW zh_CN ja; do
    locale_dir="$stage_dir/contents/locale/$language/LC_MESSAGES"
    mkdir -p "$locale_dir"
    msgfmt --check "$project_dir/po/$language.po" -o "$locale_dir/plasma_applet_com.pulipuli.applicationdashboardplus.mo"
done
python3 - "$stage_dir" "$project_dir/dist/application-dashboard-plus.plasmoid" <<'PY'
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import sys
root=Path(sys.argv[1])
with ZipFile(sys.argv[2], 'w', ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob('*')):
        if path.is_file(): archive.write(path, path.relative_to(root))
PY
printf 'Built: %s/dist/application-dashboard-plus.plasmoid\n' "$project_dir"
