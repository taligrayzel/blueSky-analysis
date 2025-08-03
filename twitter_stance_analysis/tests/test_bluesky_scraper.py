import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).parent.parent / 'src'))
from webApp.bluesky_scraper import BlueskyScraper

class TestBlueskyScraper(unittest.TestCase):
    @patch('bluesky_scraper.Client')
    def setUp(self, mock_client):
        self.mock_client = mock_client.return_value
        self.scraper = BlueskyScraper()

    def test_authenticate_with_credentials(self):
        with patch.object(self.scraper, '_load_credentials', return_value=True) as mock_load:
            self.scraper._authenticate()
            mock_load.assert_called_once()

    def test_authenticate_guest(self):
        with patch.object(self.scraper, '_load_credentials', return_value=False):
            with patch.object(self.scraper.client, 'login') as mock_login:
                self.scraper._authenticate()
                mock_login.assert_called_once()

    def test_get_user_info_success(self):
        fake_profile = MagicMock()
        fake_profile.display_name = 'Test User'
        fake_profile.description = 'desc'
        fake_profile.followers_count = 10
        fake_profile.following_count = 5
        fake_profile.posts_count = 3
        self.mock_client.get_profile.return_value = fake_profile
        info = self.scraper.get_user_info('testuser')
        self.assertEqual(info['display_name'], 'Test User')
        self.assertEqual(info['followers_count'], 10)

    def test_get_user_info_not_found(self):
        self.mock_client.get_profile.return_value = None
        info = self.scraper.get_user_info('nouser')
        self.assertIsNone(info)

    def test_get_user_posts(self):
        # Mock profile
        self.mock_client.get_profile.return_value = MagicMock()
        # Mock feed response
        mock_feed = MagicMock()
        mock_feed.feed = []
        mock_feed.cursor = None
        self.mock_client.get_author_feed.return_value = mock_feed
        posts = self.scraper.get_user_posts('testuser', max_posts=10)
        self.assertIsInstance(posts, list)

    def test_save_posts(self):
        posts = [{'id': '1', 'text': 'test', 'created_at': 'now', 'metrics': {}, 'entities': {}}]
        handle = 'testuser'
        output_file = self.scraper.RAW_DATA_DIR / f'{handle.replace(".", "_")}_posts.json'
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            self.scraper.save_posts(posts, handle)
            mock_file.assert_called_with(output_file, 'w', encoding='utf-8')

if __name__ == '__main__':
    unittest.main() 