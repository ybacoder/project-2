# if adding files to directory or db, setup method should create the test dir to hold those files
# and teardown method should delete all those for a clean slate for the next test

# import the os
import os

# import the unittest package for python
import unittest

# import app from the app.py file
from app import app


class RoutingTests(unittest.TestCase):
    # function to set up testing connection
    def set_up(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    # function to teardown connection after testing
    def test_tear_down(self):
        pass

    def test_home(self):
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_data(self):
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_timeseries(self):
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_correlation(self):
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_scrape(self):
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
