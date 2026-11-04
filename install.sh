#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
plugin_id='com.pulipuli.applicationdashboardplus'
if [[ $EUID -eq 0 ]]; then echo 'Run this script as your desktop user, without sudo.' >&2; exit 1; fi
for tool in kpackagetool5 plasmashell; do
    command -v "$tool" >/dev/null || { echo "Missing: $tool. Plasma 5.27 is required." >&2; exit 1; }
done
plasma_version="$(plasmashell --version)"
[[ $plasma_version == *' 5.27.'* ]] || { echo "Unsupported: $plasma_version. This release targets Plasma 5.27." >&2; exit 1; }
"$project_dir/build.sh"
package="$project_dir/dist/application-dashboard-plus.plasmoid"
if kpackagetool5 --type Plasma/Applet --show "$plugin_id" >/dev/null 2>&1; then
    kpackagetool5 --type Plasma/Applet --upgrade "$package"
else
    kpackagetool5 --type Plasma/Applet --install "$package"
fi
printf '\nInstalled Application Dashboard Plus. Add it from Add Widgets or Show Alternatives.\nLog out and back in after updating a loaded native plugin. Your desktop was not restarted.\n'
