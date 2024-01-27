import unittest
import routes
import requests
import json
import sys

class TestFlaskApiUsingRequests(unittest.TestCase):
    def test_login1(self):
        response = requests.get('http://127.0.0.1:5000/check/login?phone=root2')
        self.assertEqual(response.json(),'logined ')

    def test_login2(self):
        response = requests.get('http://127.0.0.1:5000/check/login?phone=79226023465')
        self.assertEqual(response.json(),'waiting_qr_login')

    def test_login3(self):
        response = requests.get('http://127.0.0.1:5000/check/login?phone=792565656565656')
        self.assertEqual(response.json(),'error')

    def test_login4(self):
        response = requests.get('http://127.0.0.1:5000/check/login?phone=gfdfgdfgdfgfd')
        self.assertEqual(response.json(),'error')



if __name__ == "__main__":
    unittest.main()