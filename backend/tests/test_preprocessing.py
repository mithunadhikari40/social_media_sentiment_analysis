import unittest
from backend.analysis import clean_text

class TestPreprocessing(unittest.TestCase):

    def test_lowercase_conversion(self):
        self.assertEqual(clean_text("HELLO"), "hello")

    def test_remove_urls_mentions_hashtags(self):
        text = "Check this https://t.co abc #fun @user"
        cleaned = clean_text(text)
        self.assertNotIn("https", cleaned)
        self.assertNotIn("#", cleaned)
        self.assertNotIn("@", cleaned)

    def test_lemmatization_and_stopwords(self):
        text = "Running runs ran easily"
        cleaned = clean_text(text)
        self.assertIn("run", cleaned)
        self.assertIn("easily", cleaned)


if __name__ == "__main__":
    unittest.main()
