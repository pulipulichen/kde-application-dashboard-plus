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
restart_plasma=true
args=()
for arg in "$@"; do
    case "$arg" in
        --no-restart) restart_plasma=false ;;
        *) args+=("$arg") ;;
    esac
done
set -- "${args[@]}"
package=''
case "${1:-}" in
    --build)
        [[ $# -eq 1 ]] || { echo 'Usage: ./install.sh [--build | --package FILE] [--no-restart]' >&2; exit 1; }
        "$project_dir/build.sh"
        package="$project_dir/dist/application-dashboard-plus.plasmoid"
        ;;
    --package)
        [[ $# -eq 2 ]] || { echo 'Usage: ./install.sh --package FILE [--no-restart]' >&2; exit 1; }
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
            download_args=("$download_dir")
            # A source checkout must install the Release built from THAT checkout.
            # An older successful build is not a valid substitute for a pending one.
            if [[ -d "$project_dir/.git" ]] && command -v git >/dev/null 2>&1; then
                checkout_commit="$(git -C "$project_dir" rev-parse HEAD)"
                download_args+=(--require-commit "$checkout_commit")
            fi
            package="$(python3 "$project_dir/download-release.py" "${download_args[@]}")"
        fi
        ;;
    *) echo 'Usage: ./install.sh [--build | --package FILE] [--no-restart]' >&2; exit 1 ;;
esac
[[ -s "$package" ]] || { echo "Package not found or empty: $package" >&2; exit 1; }
if kpackagetool5 --type Plasma/Applet --show "$plugin_id" >/dev/null 2>&1; then
    kpackagetool5 --type Plasma/Applet --upgrade "$package"
else
    kpackagetool5 --type Plasma/Applet --install "$package"
fi
# KDE 5 alternatives/widget explorer resolves an icon theme name, not the
# relative screenshot.png path in metadata. Register the packaged preview in
# the user icon theme so it works without root or a hard-coded home directory.
data_home="${XDG_DATA_HOME:-$HOME/.local/share}"
preview="$data_home/plasma/plasmoids/$plugin_id/contents/screenshot.png"
icon="$data_home/icons/hicolor/256x256/apps/$plugin_id.png"
if [[ ! -s "$preview" ]]; then
    echo "Missing bundled preview after installation: $preview" >&2
    exit 1
fi
install -Dm644 "$preview" "$icon"
printf 'Installed widget preview icon: %s\n' "$icon"
if command -v kbuildsycoca5 >/dev/null 2>&1; then
    kbuildsycoca5 --noincremental >/dev/null 2>&1 || echo 'KService cache refresh failed; Plasma restart should still reload the icon.' >&2
fi
restart_plasma_shell() {
    if [[ $restart_plasma == false ]]; then
        echo 'Plasma Shell restart skipped (--no-restart).'
        return
    fi
    if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
        echo 'No graphical session detected; Plasma Shell restart skipped.'
        return
    fi
    if command -v systemctl >/dev/null 2>&1 && systemctl --user is-active --quiet plasma-plasmashell.service; then
        if systemctl --user restart plasma-plasmashell.service; then
            echo 'Plasma Shell restarted; no logout is required.'
            return
        fi
        echo 'The Plasma Shell user service could not be restarted; trying --replace.' >&2
    fi
    if command -v pgrep >/dev/null 2>&1 && pgrep -u "$(id -u)" -x plasmashell >/dev/null 2>&1; then
        nohup plasmashell --replace </dev/null >/dev/null 2>&1 &
        disown || true
        echo 'Requested a Plasma Shell replacement; no logout is required.'
    else
        echo 'No running Plasma Shell found; restart skipped.'
        echo 'If the widget still appears outdated, run: systemctl --user restart plasma-plasmashell.service'
    fi
}
printf '\nInstalled Application Dashboard Plus. Add it from Add Widgets or Show Alternatives.\n'
restart_plasma_shell
