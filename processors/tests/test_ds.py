#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from processors import *
import os


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

'''
Testing named entity recognition.
IOB notation should be neutralized for bionlp
'''

class DSTests(unittest.TestCase):

    def test_interval(self):
        a = Interval(start=1, end=3)
        b = Interval(start=3, end=4)
        c = Interval(start=2, end=3)
        # commutative
        self.assertTrue(a.overlaps(c), "Problem detecting overlapping Intervals")
        self.assertTrue(c.overlaps(a), "Problem detecting overlapping Intervals")
        # commutative
        self.assertFalse(a.overlaps(b), "Problem detecting overlapping Intervals")
        self.assertFalse(b.overlaps(a), "Problem detecting overlapping Intervals")
        # check contains
        self.assertFalse(a.contains(b), "Problem with Interval.contains")
        self.assertTrue(a.contains(c), "Problem with Interval.contains")
        # check size
        self.assertEqual(a.size(), 2, "Problem with Interval.size")
        self.assertEqual(b.size(), 1, "Problem with Interval.size")
        self.assertEqual(c.size(), 1, "Problem with Interval.size")

if __name__ == "__main__":
    unittest.main()
