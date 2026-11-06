#!/usr/bin/env python3
import hashlib
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('downloader', Path(__file__).resolve().parents[1] / 'download-release.py')
downloader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(downloader)


class ReleaseDownloadTest(unittest.TestCase):
    def test_skip_draft_and_incomplete_accept_prerelease(self):
        assets = [{'name': downloader.PACKAGE}, {'name': 'SHA256SUMS'}]
        releases = [{'draft': True, 'assets': assets}, {'assets': assets[:1]},
                    {'tag_name': 'build-1', 'prerelease': True, 'assets': assets}]
        release, _ = downloader.select_release(releases)
        self.assertEqual(release['tag_name'], 'build-1')

    def test_release_must_match_source_commit(self):
        assets = [{'name': downloader.PACKAGE}, {'name': 'SHA256SUMS'}]
        sha_old, sha_new = 'a' * 40, 'b' * 40
        releases = [
            {'tag_name': 'old', 'target_commitish': sha_old, 'assets': assets},
            {'tag_name': 'new', 'target_commitish': sha_new, 'assets': assets},
        ]
        release, _ = downloader.select_release(releases, required_commit=sha_new)
        self.assertEqual(release['tag_name'], 'new')
        with self.assertRaisesRegex(ValueError, 'not published yet'):
            downloader.select_release(releases, required_commit='c' * 40)

    def test_missing_release_is_clear(self):
        with self.assertRaisesRegex(ValueError, 'No finished amd64 release'):
            downloader.select_release([])

    def test_checksum_match_and_corruption(self):
        data = b'precompiled-package'
        checksums = hashlib.sha256(data).hexdigest() + '  ' + downloader.PACKAGE + '\n'
        downloader.verify(data, checksums)
        with self.assertRaisesRegex(ValueError, 'does not match'):
            downloader.verify(data + b'corruption', checksums)
        with self.assertRaisesRegex(ValueError, 'missing from SHA256SUMS'):
            downloader.verify(data, checksums.replace(downloader.PACKAGE, 'other.plasmoid'))


if __name__ == '__main__':
    unittest.main()
