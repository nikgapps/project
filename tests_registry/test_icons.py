import unittest
from nikgapps_registry.icons import image_extension

class IconFormatTest(unittest.TestCase):
    def test_supported_image_signatures(self):
        self.assertEqual("png", image_extension(b"\x89PNG\r\n\x1a\n"))
        self.assertEqual("jpg", image_extension(b"\xff\xd8\xff"))
        self.assertEqual("webp", image_extension(b"RIFF1234WEBP"))

    def test_rejects_html_or_vector_response(self):
        for data in (b"<html>sign in</html>", b"<svg></svg>", b""):
            with self.assertRaises(ValueError): image_extension(data)
