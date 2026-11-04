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
ET.parse(package / 'contents/config/main.xml')
for name in ('main.qml', 'ConfigGeneral.qml'):
    text = (package / 'contents/ui' / name).read_text()
    assert 'org.kde.plasma.kickerdash' not in text
    assert metadata['KPlugin']['Id'] in text
for path in package.rglob('*.qml'):
    for local_import in re.findall(r'^import "([^"]+)"', path.read_text(), re.M):
        assert (path.parent / local_import).exists(), (path, local_import)
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
