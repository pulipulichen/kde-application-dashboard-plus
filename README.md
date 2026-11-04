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

## Install a precompiled Release (recommended)

Open [GitHub Releases](https://github.com/pulipulichen/kde-application-dashboard-plus/releases)
and download **application-dashboard-plus-kubuntu24.04-amd64.tar.gz** from the newest
completed build. Extract it, open the extracted folder in a terminal, then run:

```bash
./install.sh
```

The archive includes the compiled native plugin and translations. Installing it
needs no compiler, CMake, sudo, apt update, development packages, or network access.
It uses the Plasma 5 runtime already installed on Kubuntu. Do not run it as root.
Prebuilt releases currently target **amd64 / Kubuntu 24.04 / Plasma 5.27 / X11**.

If you already cloned this repository:

```bash
git pull --ff-only
./install.sh
```

Without a bundled package, the installer downloads the newest complete Release
(including development prereleases) and verifies its SHA-256 checksum. It does
not compile locally. You do not need to run `install-deps.sh` for normal installation.

The standalone `.plasmoid` is also available as a Release asset:

```bash
./install.sh --package /path/to/application-dashboard-plus-kubuntu24.04-amd64.plasmoid
```

Right-click your panel → **Add Widgets** → search for **Application Dashboard
Plus**, then add it. Alternatively use **Show Alternatives** on your launcher
if offered. You can set its keyboard shortcut in the normal Plasma configuration.
The original KDE launcher remains installed.

## GitHub Actions builds

Pushes to `main`, version tags, and manual workflow runs build on **ubuntu-24.04**,
run the Qt and package checks, then publish a `.plasmoid`, an installer `.tar.gz`,
and `SHA256SUMS` directly to **Releases**. No Actions artifacts are uploaded.
Development builds get unique prerelease tags; version tags get matching Releases.

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

## Build from source (developers only)

```bash
./install-deps.sh
./build.sh
# Optional: install your locally compiled package
./install.sh --build
```

Only this developer path needs CMake, a C++17 compiler, Qt 5.15 development
packages, KF5WindowSystem development headers, gettext and Python 3. The
`install-deps.sh` script uses sudo and apt to install those build dependencies.

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
