import json
import requests
import unittest

#from common.logger import get_logger

#_log = get_logger('test')


class TestCasesForDispatchTaskAPI(unittest.TestCase):

    def setUp(self):
        print(f'\n ----- {self.id()}, case BEGIN')


    def tearDown(self):
        print('case END')


    def test_basic_body(self):
        body = {
            'urls': ['http://a.com', 'http://b.com','http://c.com'],
        }

        resp = requests.get('http://127.0.0.1:8000/urls/contents', json=body)
        print(f'resp: {json.dumps(resp.json(), indent=2)}\n')

        self.assertTrue(resp.text)
        self.assertIsInstance(resp.json(), dict)
        self.assertEqual(resp.status_code, 200)

    def test_invalid_urls_body(self):
        body = {
            'urls': ['com', 'http://b.com','http://c.com'],
        }

        resp = requests.get('http://127.0.0.1:8000/urls/contents', json=body)
        print(f'resp: {resp.text}\n')

        self.assertTrue(resp.text)
        self.assertIsInstance(resp.json(), dict)
        self.assertEqual(resp.status_code, 422)

    def test_empty_urls_body(self):
        body = {
            'urls': [],
        }

        resp = requests.get('http://127.0.0.1:8000/urls/contents', json=body)
        print(f'resp: {resp.text}\n')

        self.assertTrue(resp.text)
        self.assertIsInstance(resp.json(), dict)
        self.assertEqual(resp.status_code, 422)

    def test_none_urls_body(self):
        body = {
            #'urls': None,
        }

        resp = requests.get('http://127.0.0.1:8000/urls/contents', json=body)
        print(f'resp: {resp.text}\n')

        self.assertTrue(resp.text)
        self.assertIsInstance(resp.json(), dict)
        self.assertEqual(resp.status_code, 422)


    def test_only_without_max_words(self):
        body = {"sid": "test", "urls": ["https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html"]}

        resp = requests.get('http://127.0.0.1:8000/urls/contents', json=body)
        print(f'resp: {json.dumps(resp.json(), indent=2)}\n')

        self.assertTrue(resp.text)
        self.assertIsInstance(resp.json(), dict)
        self.assertEqual(resp.status_code, 200)

if __name__ == '__main__':
    unittest.main()
