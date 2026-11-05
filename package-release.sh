#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$project_dir"
[[ $(uname -m) == x86_64 ]] || { echo 'This release bundle targets amd64.' >&2; exit 1; }
test -s dist/application-dashboard-plus.plasmoid
asset_name='application-dashboard-plus-kubuntu24.04-amd64'
stage_dir="$(mktemp -d "$project_dir/dist/installer.XXXXXXXX")"
trap 'rm -rf -- "$stage_dir"' EXIT
bundle_dir="$stage_dir/application-dashboard-plus"
mkdir -p "$bundle_dir"
cp dist/application-dashboard-plus.plasmoid "dist/$asset_name.plasmoid"
cp "dist/$asset_name.plasmoid" install.sh uninstall.sh download-release.py LICENSE UPSTREAM.md "$bundle_dir/"
cat > "$bundle_dir/INSTALL.txt" <<'NOTES'
Application Dashboard Plus — Kubuntu 24.04 / Plasma 5.27 / Qt 5.15 / X11 / amd64

In this extracted folder, open a terminal and run:
    ./install.sh

No compiler, CMake, sudo, apt update, or network access is required.
Add Application Dashboard Plus from Plasma's Add Widgets afterward.
Installer restarts Plasma Shell automatically after installation (no logout needed).
Use ./install.sh --no-restart to skip the desktop restart.
To uninstall: ./uninstall.sh

Source and updates:
https://github.com/pulipulichen/kde-application-dashboard-plus
NOTES
tar -czf "dist/$asset_name.tar.gz" -C "$stage_dir" application-dashboard-plus
(cd dist && sha256sum "$asset_name.plasmoid" "$asset_name.tar.gz" > SHA256SUMS)
echo "Prepared dist/$asset_name.tar.gz and SHA256SUMS"
