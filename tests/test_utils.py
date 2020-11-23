# -*- coding: utf-8 -*-
"""
Test the utilities.
"""
import unittest
from weather_collector.caller import _set_attr_if_exist


class TestSetAttr(unittest.TestCase):
    """Test set attribute"""

    def test_set_attr(self):
        """Test setting attribute if it exists"""

        # pylint: disable=too-few-public-methods
        class TestClass:
            """Test class"""
            def __init__(self, **kwargs):
                self.attr1 = None
                _set_attr_if_exist(self, kwargs)

        obj = TestClass(attr1=1, attr2=2)
        self.assertEqual(obj.attr1, 1)
        self.assertFalse(hasattr(obj, 'attr2'))
