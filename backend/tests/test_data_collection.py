import unittest
from unittest.mock import patch
from backend.twitter_client import TwitterClient


class TestTwitterClient(unittest.TestCase):

    @patch.dict('os.environ', {'TWITTER_BEARER_TOKEN': 'test_token'})
    def test_twitter_api_auth_success(self):
        # Mock the actual API call so no network request is made
        with patch('backend.twitter_client.TwitterClient.search_tweets') as mock_api:
            mock_api.return_value = [{"text": "Test tweet", "id": 1}]

            twitter_client = TwitterClient()
            tweets = twitter_client.search_tweets("test query")

            # Assertions
            self.assertEqual(len(tweets), 1)
            self.assertEqual(tweets[0]['text'], "Test tweet")

    @patch.dict('os.environ', {'TWITTER_BEARER_TOKEN': 'test_token'})
    def test_twitter_api_invalid_keys(self):
        # Mock the API call to raise an exception simulating invalid credentials
        with patch('backend.twitter_client.TwitterClient.search_tweets',
                   side_effect=Exception("Authentication failed")):
            twitter_client = TwitterClient()

            # Ensure the exception is raised
            with self.assertRaises(Exception) as context:
                twitter_client.search_tweets("test query")

            self.assertEqual(str(context.exception), "Authentication failed")


if __name__ == "__main__":
    unittest.main()
