#!/usr/bin/env python3
"""Download the newest complete amd64 Release package, including prereleases."""
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen

REPOSITORY = 'pulipulichen/kde-application-dashboard-plus'
PACKAGE = 'application-dashboard-plus-kubuntu24.04-amd64.plasmoid'


def fetch(url):
    request = Request(url, headers={'User-Agent': 'dashboard-plus-installer', 'Accept': 'application/vnd.github+json' if 'api.github.com' in url else 'application/octet-stream'})
    with urlopen(request, timeout=45) as response:
        return response.read()


def select_release(releases, required_commit=None):
    for release in releases:
        if release.get('draft'):
            continue
        # Do not silently install an older build after `git pull` updated the source.
        if required_commit and release.get('target_commitish') != required_commit:
            continue
        assets = {item['name']: item for item in release.get('assets', [])}
        if PACKAGE in assets and 'SHA256SUMS' in assets:
            return release, assets
    if required_commit:
        raise ValueError('The Release for source commit ' + required_commit[:12]
                         + ' is not published yet. Check https://github.com/' + REPOSITORY
                         + '/actions and rerun ./update.sh when that build succeeds;'
                         + ' the currently installed version was left unchanged.')
    raise ValueError('No finished amd64 release is available yet. Check https://github.com/' + REPOSITORY + '/actions')


def verify(data, checksum_text):
    for line in checksum_text.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2 and parts[1].lstrip('*') == PACKAGE:
            if hashlib.sha256(data).hexdigest() != parts[0]:
                raise ValueError('Package SHA-256 does not match the Release checksum.')
            return
    raise ValueError('Package is missing from SHA256SUMS.')


def main():
    if len(sys.argv) not in (2, 4) or (len(sys.argv) == 4 and sys.argv[2] != '--require-commit'):
        raise ValueError('Usage: download-release.py DESTINATION [--require-commit SHA]')
    destination = Path(sys.argv[1])
    required_commit = sys.argv[3] if len(sys.argv) == 4 else None
    releases = json.loads(fetch('https://api.github.com/repos/' + REPOSITORY + '/releases?per_page=30'))
    release, assets = select_release(releases, required_commit)
    print('Downloading ' + release['tag_name'] + ' (commit ' + str(release.get('target_commitish')) + ') from GitHub Releases…', file=sys.stderr)
    data = fetch(assets[PACKAGE]['browser_download_url'])
    verify(data, fetch(assets['SHA256SUMS']['browser_download_url']).decode('utf-8'))
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / PACKAGE
    path.write_bytes(data)
    print(path)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('Download failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
