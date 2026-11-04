# Changelog

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
