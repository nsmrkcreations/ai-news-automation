import unittest
from src.core.gdelt_provider import GdeltNewsProvider

class TestGdeltProvider(unittest.TestCase):
    def test_init(self):
        """Test provider initialization"""
        provider = GdeltNewsProvider()
        self.assertEqual(provider.name, "GDELT")
        self.assertTrue(provider.is_available)
        self.assertIsNone(provider.last_error)
        self.assertEqual(provider.base_url, "https://api.gdeltproject.org/api/v2/doc/doc")

if __name__ == '__main__':
    unittest.main()
