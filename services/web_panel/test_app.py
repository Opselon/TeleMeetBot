import unittest
import os
from web_panel import app
import database
from unittest.mock import patch

class TeleMeetBotTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Mock the database functions
        self.mock_db = {
            'telegram_token': '',
            'meet_url': '',
            'youtube_url': ''
        }
        self.get_config_patch = patch('database.get_config', side_effect=lambda key: self.mock_db.get(key))
        self.set_config_patch = patch('database.set_config', side_effect=lambda key, value: self.mock_db.update({key: value}))

        self.mock_get_config = self.get_config_patch.start()
        self.mock_set_config = self.set_config_patch.start()


    def tearDown(self):
        self.get_config_patch.stop()
        self.set_config_patch.stop()

    def test_index_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'TeleMeet Bot Control Panel', response.data)

    def test_save_token(self):
        response = self.app.post('/save_token', data={'token': 'test_token'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Telegram token saved successfully.', response.data)
        self.assertEqual(self.mock_db['telegram_token'], 'test_token')

    def test_deploy(self):
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            response = self.app.post('/deploy', data={'meet_url': 'https://meet.google.com/test'}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Deploying bot to Google Meet.', response.data)
            self.assertEqual(self.mock_db['meet_url'], 'https://meet.google.com/test')

    def test_play(self):
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            response = self.app.post('/play', data={'youtube_url': 'https://www.youtube.com/watch?v=test'}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Playing YouTube video.', response.data)
            self.assertEqual(self.mock_db['youtube_url'], 'https://www.youtube.com/watch?v=test')

    def test_stop(self):
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            response = self.app.post('/stop', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Stopping automation and leaving the meeting.', response.data)

    def test_status(self):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = [
                unittest.mock.Mock(status_code=200, json=lambda: {'status': 'online'}),
                unittest.mock.Mock(status_code=200, json=lambda: {'status': 'online'})
            ]
            response = self.app.get('/status')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {
                'telegram_bot': 'online',
                'selenium_automation': 'online'
            })

if __name__ == '__main__':
    unittest.main()
