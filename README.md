# Application Dashboard Plus

A fullscreen application launcher for **Kubuntu 24.04, KDE Plasma 5.27 and Qt 5.15
on X11**, based on KDE's Application Dashboard. It installs alongside the original
launcher under the separate ID `com.pulipuli.applicationdashboardplus`.

- A visible search field receives focus immediately, supports Chinese input
  through your existing Qt-compatible input method, and searches committed text.
- Search results do not steal the editor's focus while you compose characters.
- Opening another Plus dashboard closes the previous one, including instances
  in other panels or screens in the same plasmashell process.
- Switching virtual desktops closes the dashboard.
- Favorites, categories, KRunner results, widgets and launcher configuration
  retain the upstream interface. Favorites use a separate namespace.
- English, Traditional Chinese, Simplified Chinese and Japanese UI catalogs.

## Install

Run these commands in a terminal **as your desktop user**:

```bash
git clone https://github.com/pulipulichen/kde-application-dashboard-plus.git
cd kde-application-dashboard-plus
./install-deps.sh
./install.sh
```

`install-deps.sh` uses sudo to install build dependencies. `install.sh` builds and
tests a small Qt 5 native QML plugin, compiles translations, packages the widget,
and installs it for your user using `kpackagetool5`. It never restarts Plasma.
The native plugin is contained inside the widget, without system-wide libraries
or a background service. Build tools: C++17 compiler, CMake, Qt 5.15 development
packages, KF5WindowSystem development package, gettext and Python 3.

Right-click your panel → **Add Widgets** → search for **Application Dashboard
Plus**, then add it. Alternatively use **Show Alternatives** on your launcher
if offered. Keep the original launcher until you have checked the new one.
The regular Plasma/Kicker runtime packages must remain installed. You can set
the widget's keyboard shortcut in its normal Plasma configuration dialog.

## Use

Open the launcher and type using your normal Chinese input method. The input
method must already work in other Qt applications; this widget does not install
or reconfigure Fcitx/IBus. Chinese input support does not add translation,
phonetic matching, or Traditional/Simplified query conversion to KRunner.

- Down or Tab from the editor: move to results; arrows navigate as usual.
- Enter from the editor: activate the first application/document search result.
- Enter during composition belongs to the input method for selecting characters.
- Escape: cancel composition through the input method; outside composition,
  clear the search first, then close the dashboard on the next Escape.
- Click the clear button to clear the query and return focus to the editor.

Exclusive opening applies to **Plus instances in one plasmashell process**.
Unmodified KDE launchers and independently launched test processes are outside
that scope. Focus loss alone does not force the dashboard closed, so an input
method's candidate popup can work without fighting the launcher.

## Update and uninstall

```bash
./update.sh
./uninstall.sh
```

Update requires a clean `main` checkout and uses `git pull --ff-only`.
After updating a widget whose native plugin has already been loaded, **log out
and back in** to load the new binary. Uninstall only removes this widget; it
preserves user configuration and other launchers.

## Build and validation

```bash
./build.sh
```

Output: `dist/application-dashboard-plus.plasmoid`. Build it on the target
architecture (the native library is architecture specific). The archive root
contains `metadata.json` and `contents/`, ready for `kpackagetool5`.

The build runs Qt tests for full Dashboard QML component loading, exclusive opening across independent QML engines,
owner destruction, closing on a desktop-change callback, Unicode IME
preedit/commit delivery, and typing after grid navigation. Package checks cover
metadata, configuration XML, imports and translation source coverage.

Real Fcitx/IBus candidate selection, desktop switching with KWin, multiple
screens, and installed panel/shortcut behavior also require a desktop session.
Plasma 6 and Wayland are not supported targets for this first release.

## Credits

Derived from KDE Plasma Desktop v5.27.12 by Eike Hein and KDE contributors.
See [UPSTREAM.md](UPSTREAM.md) for provenance and translator credits.
GPL-3.0-or-later; original GPL-2.0-or-later file notices are retained.
