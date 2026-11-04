#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
plugin_id='com.pulipuli.applicationdashboardplus'
asset_name='application-dashboard-plus-kubuntu24.04-amd64.plasmoid'
if [[ $EUID -eq 0 ]]; then echo 'Run this script as your desktop user, without sudo.' >&2; exit 1; fi
for tool in kpackagetool5 plasmashell; do
    command -v "$tool" >/dev/null || { echo "Missing: $tool. Plasma 5.27 is required." >&2; exit 1; }
done
plasma_version="$(env -u SESSION_MANAGER plasmashell --version)"
[[ $plasma_version == *' 5.27.'* ]] || { echo "Unsupported: $plasma_version. This release targets Plasma 5.27." >&2; exit 1; }
package=''
case "${1:-}" in
    --build)
        [[ $# -eq 1 ]] || { echo 'Usage: ./install.sh [--build | --package FILE]' >&2; exit 1; }
        "$project_dir/build.sh"
        package="$project_dir/dist/application-dashboard-plus.plasmoid"
        ;;
    --package)
        [[ $# -eq 2 ]] || { echo 'Usage: ./install.sh --package FILE' >&2; exit 1; }
        package="$2"
        ;;
    '')
        [[ $(uname -m) == x86_64 ]] || { echo 'Prebuilt packages currently support amd64 only. Build with ./install.sh --build on other architectures.' >&2; exit 1; }
        if [[ -f "$project_dir/$asset_name" ]]; then
            # Installer archive: install its bundled, precompiled package offline.
            package="$project_dir/$asset_name"
        else
            command -v python3 >/dev/null || { echo 'python3 is required to download the Release.' >&2; exit 1; }
            download_dir="$(mktemp -d)"
            trap 'rm -rf -- "$download_dir"' EXIT
            package="$(python3 "$project_dir/download-release.py" "$download_dir")"
        fi
        ;;
    *) echo 'Usage: ./install.sh [--build | --package FILE]' >&2; exit 1 ;;
esac
[[ -s "$package" ]] || { echo "Package not found or empty: $package" >&2; exit 1; }
if kpackagetool5 --type Plasma/Applet --show "$plugin_id" >/dev/null 2>&1; then
    kpackagetool5 --type Plasma/Applet --upgrade "$package"
else
    kpackagetool5 --type Plasma/Applet --install "$package"
fi
printf '\nInstalled Application Dashboard Plus. Add it from Add Widgets or Show Alternatives.\nLog out and back in after updating a loaded native plugin. Your desktop was not restarted.\n'
