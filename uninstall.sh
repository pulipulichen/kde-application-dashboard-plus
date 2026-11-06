#!/usr/bin/env bash
set -euo pipefail
if [[ $EUID -eq 0 ]]; then echo 'Run as your desktop user, without sudo.' >&2; exit 1; fi
command -v kpackagetool5 >/dev/null || { echo 'kpackagetool5 is required.' >&2; exit 1; }
plugin_id='com.pulipuli.applicationdashboardplus'
if kpackagetool5 --type Plasma/Applet --show "$plugin_id" >/dev/null 2>&1; then
    kpackagetool5 --type Plasma/Applet --remove "$plugin_id"
else
    echo 'Application Dashboard Plus is already uninstalled.'
fi
icon="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps/$plugin_id.png"
if [[ -f "$icon" ]]; then
    rm -f -- "$icon"
    echo 'Removed the widget preview from the user icon theme.'
fi
echo 'Only Application Dashboard Plus was removed. Restart Plasma Shell to unload its native plugin.'
