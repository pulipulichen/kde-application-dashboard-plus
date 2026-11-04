# Upstream provenance and licensing

The `package/` QML, JavaScript and configuration files are derived from KDE
Plasma Desktop's Kicker package, tag **v5.27.12**, commit
`3b307004e4038169329fbf5f7daf5bb15f125fd3`:

https://github.com/KDE/plasma-desktop/tree/v5.27.12/applets/kicker/package

`po/{zh_TW,zh_CN,ja}.po` come from the same tag's
`po/<locale>/plasma_applet_org.kde.plasma.kicker.po`. Original copyright,
translator credits and SPDX headers are retained. Original files are licensed
GPL-2.0-or-later; this combined derivative is distributed under GPL-3.0-or-later,
as permitted by that license. See LICENSE.

The new native window implementation replaces the original DashboardWindow.
Its API is compatible with the upstream QML, but it never raises itself on
FocusOut, has process-wide exclusive opening, closes on virtual desktop changes,
and retains focus in a visible input editor. The KDE source used for comparison:
https://github.com/KDE/plasma-workspace/blob/Plasma/5.27/applets/kicker/plugin/dashboardwindow.cpp

The installed KDE private Kicker QML plugin remains a runtime dependency.
It is not copied or rebuilt by this repository. This release targets Plasma
5.27 / Qt 5.15; private APIs do not promise compatibility with Plasma 6.
