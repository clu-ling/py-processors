#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from processors import *
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class DocumentSerializationTests(unittest.TestCase):

    def test_load_from_json(self):
        "Document.load_from_JSON should produce a Document from serialized_doc.json"
        json_file = os.path.join(__location__, "serialized_doc.json")
        print(json_file)
        with open(json_file, "r") as jf:
            doc = Document.load_from_JSON(json.load(jf))
        self.assertTrue(isinstance(doc, Document), "Document.load_from_JSON did not produce a Document from {}".format(json_file))

if __name__ == "__main__":
    unittest.main()
