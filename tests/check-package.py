#!/usr/bin/env python3
"""Check IDs, schema, local QML imports, and translation coverage before packing."""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
package = root / 'package'
metadata = json.loads((package / 'metadata.json').read_text())
assert metadata['KPlugin']['Id'] == 'com.pulipuli.applicationdashboardplus'
assert (package / 'contents' / metadata['X-Plasma-MainScript']).is_file()
# The widget picker/alternatives preview is bundled in the plasmoid.
preview = package / 'contents/screenshot.png'
assert preview.is_file() and preview.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
assert metadata['KPlugin']['Icon'] == metadata['KPlugin']['Id']
dashboard = (package / 'contents/ui/DashboardRepresentation.qml').read_text()
assert 'background: Rectangle {' in dashboard
# Empty search (even when focused) has no outline or background.
# Non-empty search gets a subtle translucent fill without an outline.
search_field = dashboard.split('id: searchField', 1)[1].split('id: cancelSearchButton', 1)[0]
assert 'color: searchField.text.length ? Qt.rgba(1, 1, 1, 0.08) : "transparent"' in search_field
assert 'border.width: 0' in search_field
assert 'searchField.activeFocus ? 1 : 0' not in search_field
# The search box must track the Applications grid when screen size changes.
assert 'x: middleRow.x + mainColumn.x' in search_field
assert 'width: mainColumnLabelUnderline.width' in search_field
assert 'anchors.horizontalCenter: parent.horizontalCenter' not in search_field
# The clear affordance must be an accessible, keyboard-operable circle/X.
clear_button = dashboard.split('id: cancelSearchButton', 1)[1].split('id: middleRow', 1)[0]
assert 'Accessible.role: Accessible.Button' in clear_button
assert 'Accessible.name: i18n("Clear search")' in clear_button
assert 'radius: width / 2' in clear_button
# Style A: subtle filled grey circle, a thicker white X, and no outlined frame.
assert 'border.width: 0' in clear_button
assert 'border.color:' not in clear_button
assert 'Qt.rgba(1, 1, 1, 0.22)' in clear_button
assert 'Qt.rgba(1, 1, 1, 0.30)' in clear_button
assert 'color: "white"' in clear_button
assert 'width: parent.width * 0.44' in clear_button
assert 'rotation: index === 0 ? 45 : -45' in clear_button
assert 'visible: searchField.text !== ""' in clear_button
assert 'iconName: "edit-clear"' not in clear_button
assert 'onClicked: cancelSearchButton.clearSearch()' in clear_button
assert 'Qt.Key_Space' in clear_button and 'Qt.Key_Return' in clear_button
ET.parse(package / 'contents/config/main.xml')
for name in ('main.qml', 'ConfigGeneral.qml'):
    text = (package / 'contents/ui' / name).read_text()
    assert 'org.kde.plasma.kickerdash' not in text
    assert metadata['KPlugin']['Id'] in text
for path in package.rglob('*.qml'):
    for local_import in re.findall(r'^import "([^"]+)"', path.read_text(), re.M):
        assert (path.parent / local_import).exists(), (path, local_import)
# A dynamically created QML DashboardWindow cannot bind to a strictly typed
# DashboardWindow property in Plasma 5.27; activation must also be null-safe.
compact = (package / 'contents/ui/CompactRepresentation.qml').read_text()
assert 'readonly property var dashWindow:' in compact
assert 'readonly property DashboardPlus.DashboardWindow dashWindow:' not in compact
assert 'function toggleDashboard()' in compact
assert compact.count('root.toggleDashboard();') == 2
# All source strings and context strings must be present in every locale.
strings = set()
for path in package.rglob('*'):
    if path.suffix in ('.qml', '.js'):
        strings.update(re.findall(r'\bi18n\("((?:[^"\\]|\\.)*)"', path.read_text()))
        strings.update(re.findall(r'\bi18nc\("(?:[^"\\]|\\.)*",\s*"((?:[^"\\]|\\.)*)"', path.read_text()))
for language in ('zh_TW', 'zh_CN', 'ja'):
    po = (root / 'po' / (language + '.po')).read_text()
    for string in strings:
        assert ('msgid "' + string + '"') in po, (language, string)
    assert '"Language: ' + language + '\\n"' in po
print(f'Package checks passed; {len(strings)} source strings in all three translation catalogs (English is the source language).')
