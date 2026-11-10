from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from NikGapps.helper.compression.CompOps import CompOps


class CompressionSizeTests(unittest.TestCase):
    def test_sizes_use_archived_line_endings_and_include_generated_permission_xml(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for label, newline in (('windows', '\r\n'), ('linux', '\n')):
                file = root / (label + '.xml')
                # CRLF crosses a KiB boundary; both archives contain 1020 LF bytes.
                file.write_bytes(('x' + newline).encode() * 510)
                package = Mock(file_dict={file: '___etc___permissions/test.xml'}, clean_flash_only=False,
                    priv_app_permissions_str='p' * 1025, package_name='com.example', pkg_size=0)
                archive = Mock()
                with patch.object(CompOps, 'get_compression_obj', return_value=archive):
                    self.assertTrue(CompOps.compress_package(str(root / (label + '.zip')), package))
                self.assertEqual(3, package.pkg_size)
                self.assertEqual('3', (root / (label + '_zip.txt')).read_text().strip())
