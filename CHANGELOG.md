# Changelog

## 0.1.4 — 2026-11-06 — Preview icon and understated search field

- Use the bundled `contents/screenshot.png` as the widget picker/alternatives
  preview by referencing it in the plugin's icon metadata.
- Replace the dashboard search field's solid dark background with a transparent
  background and a faint outline only while the search field has focus.
- Retain the initial favorite focus, type-to-search, navigation and IME behavior.
- Check the screenshot and visual style in the package regression checks.

## 0.1.3 — 2026-11-05 — Reload Plasma Shell automatically after install/update

- Restart only the user's Plasma Shell after a successful installation or update,
  keeping other applications running and avoiding a full KDE logout/login.
- Prefer `systemctl --user restart plasma-plasmashell.service` when it is an
  active user service; otherwise request `plasmashell --replace` for an existing
  shell process. Skip desktop reloads when running without a graphical session.
- Allow `./install.sh --no-restart` and `./update.sh --no-restart` (including
  alongside `--build` or `--package FILE`) for troubleshooting or remote use.
- Add installer restart regression tests, document behavior, and update the
  Release bundle instructions.


## 0.1.2 — 2026-11-05 — Fix dashboard window activation

A Kubuntu 24.04 / Plasma 5.27.12 / X11 report showed that the launcher icon was
present, but clicking it opened no dashboard. The plasmoid log identified:

`CompactRepresentation.qml:27:5: Unable to assign DashboardRepresentation_QMLTYPE_* to DashboardWindow`

- Store the dynamically instantiated QML-derived window in a `var` property,
  rather than a strictly declared C++ `DashboardWindow` type.
- Route mouse and keyboard activation through one guarded toggle function,
  avoiding a secondary JavaScript exception when window creation fails.
- Add a Qt QML regression case for the dynamic derived-window assignment and
  a package check for the launcher property and guarded activation paths.
- Rebuild and publish precompiled Plasma 5 assets to GitHub Releases. Existing
  users should log out and in after upgrading to unload the previous native plugin.


## 0.1.1 — 2026-11-05 — Precompiled Release installation

Observed user installation failure: an unrelated Pinta PPA returned `403 Forbidden`
during `apt-get update`. Because install-deps.sh stops on errors, build dependencies
were not installed, and install.sh then reported `Missing dependency: cmake`.
The default local-build installation flow was unsuitable for end users.

- Add an ubuntu-24.04 GitHub Actions job to build/test and publish directly to
  Releases, without Actions artifact storage. Main/manual builds use unique
  prerelease tags; version tags publish matching Releases.
- Publish the amd64 .plasmoid, a self-contained installer .tar.gz, and SHA256SUMS.
- Default install.sh to the bundled prebuilt package or a checksum-verified
  download of the newest complete Release. No local compilation or apt update.
- Keep explicit `--build` for developers and `--package FILE` for local packages.
- Document archive extraction and ./install.sh as the recommended installation.
- Preserve existing apt sources; this change does not modify the user's Pinta
  or duplicate Cursor repositories.

Validation: shell syntax, YAML structure, Release selection/checksum logic and
local installer archive checks are performed before publication. GitHub Actions run #1 succeeded:
https://github.com/pulipulichen/kde-application-dashboard-plus/actions/runs/41903603658

Build source commit: `776835d1df7efc758a600b13fa89fd7bf81e6ed3`.
The native Qt suite, three downloader unit tests, package checks and translation
compilation passed on the hosted ubuntu-24.04 runner. Release publishing passed.

Verified published Release:
https://github.com/pulipulichen/kde-application-dashboard-plus/releases/tag/build-1-1-776835d

Assets confirmed through the GitHub Releases API:
- application-dashboard-plus-kubuntu24.04-amd64.plasmoid — 621277 bytes
- application-dashboard-plus-kubuntu24.04-amd64.tar.gz — 633348 bytes
- SHA256SUMS — 240 bytes

Real KWin/IME/multi-monitor desktop acceptance checks remain as documented in
`tests/MANUAL.md`; CI publication does not replace those checks.

## 0.1.0 — 2026-11-05

Initial Plasma 5.27 / Qt 5.15 / X11 implementation for Kubuntu 24.04.

- Vendor KDE Kicker's QML package at v5.27.12, preserving provenance and licenses.
- Install as a separate launcher, retaining the original dashboard.
- Replace the hidden search editor with a visible Plasma Components 3 TextField.
- Keep focus in the editor while KRunner asynchronously updates results.
- Search committed Unicode text; leave IME composition and candidate-selection
  keys to Qt's input context. Add Down/Tab result navigation and Enter activation.
- Replace the original native window's key-event ping-pong and FocusOut
  reactivation with a small packaged Qt 5 QML extension.
- Make opening exclusive across plugin instances and independent QML engines in
  the same process; close on virtual desktop changes. Place each reopened window
  on the current desktop and the launching panel's screen.
- Include upstream Traditional Chinese, Simplified Chinese and Japanese catalogs.
- Add executable dependency, build, install, update and uninstall scripts.
- Add native regression tests and package/translation checks.

### Engineering notes

A QML-only patch is insufficient for this version: the stock native
DashboardWindow reactivates itself on FocusOut and temporarily restores grid
focus after forwarding a key. Both behaviors conflict with input methods and
multiple fullscreen launchers. The new window implementation avoids those paths.

Validation on Ubuntu 24.04 / Qt 5.15.13 / KF5 5.115:

- Native plugin compiled successfully with GCC 13.3.
- All four Qt test cases passed: full Dashboard QML component loading,
  exclusive opening across QML engines and owner destruction, desktop-change
  close callback, and Chinese preedit/commit with focus retention/typeahead.
- All QML files passed qmllint syntax checks; all five scripts passed bash -n.
- Metadata, configuration XML, local imports and 36 UI source strings in all
  three translation catalogs passed checks; msgfmt --check passed.
- Built the architecture-specific .plasmoid with the native plugin and all
  three compiled catalogs at the correct archive root.

A full KWin session could not be launched in the test environment (D-Bus sockets
are unavailable). Actual desktop-change signal delivery, panel/shortcut behavior,
Fcitx/IBus candidate popups and multi-monitor placement remain manual QA items.
See tests/MANUAL.md.

Build fixes caught by validation: Qt 5 moc needs a separate no-argument notify
signal for the backgroundColor alias; local native directory imports need an
explicit 1.0 import and must omit a fixed module identifier because Plasma
resolves the directory URI from the package path. The full Dashboard load test
covers the latter, which isolated window tests alone would miss.
