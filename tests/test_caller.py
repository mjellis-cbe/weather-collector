# -*- coding: utf-8 -*-
"""
Tests API Caller
"""
import unittest
from weather_collector.caller import Caller

from .helpers import (
    get_example_response,
    get_example_weather_config,
)

__author__ = "Matt Ellis"
__copyright__ = "Matt Ellis"
__license__ = "mit"


class TestCaller(unittest.TestCase):
    """Test API caller"""

    @classmethod
    def setUpClass(cls):
        cls.config = get_example_weather_config()
        cls.response = get_example_response()

    def test_bad_config(self):
        """Test bad configuration"""
        caller = Caller(config={'blah': 1})
        with self.assertRaises(KeyError):
            caller.call_api()

    def test_call_api(self):
        """Test call OpenWeather API"""
        caller = Caller(config=self.config)
        data = caller.call_api()
        self.assertIn('CallTime', data)
        self.assertIn('Response', data)
        self.assertTrue(isinstance(data['Response'], dict))


if __name__ == '__main__':
    unittest.main()
