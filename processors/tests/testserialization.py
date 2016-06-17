#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from processors import *
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class DocumentSerializationTests(unittest.TestCase):

    def test_doc_load_from_json(self):
        "Document.load_from_JSON should produce a Document from serialized_doc.json"
        json_file = os.path.join(__location__, "serialized_doc.json")
        print(json_file)
        with open(json_file, "r") as jf:
            doc = Document.load_from_JSON(json.load(jf))
        self.assertTrue(isinstance(doc, Document), "Document.load_from_JSON did not produce a Document from {}".format(json_file))

    def test_sentence_load_from_json(self):
        "Sentence.load_from_JSON should produce a Sentence from serialized_sentence.json"
        json_file = os.path.join(__location__, "serialized_sentence.json")
        print(json_file)
        with open(json_file, "r") as jf:
            s = Sentence.load_from_JSON(json.load(jf))
        self.assertTrue(isinstance(s, Sentence), "Sentence.load_from_JSON did not produce a Sentence from {}".format(json_file))
        
if __name__ == "__main__":
    unittest.main()
