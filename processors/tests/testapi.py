#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from processors import *

port = 8886
# initialize the server
api = ProcessorsAPI(port)

class ProcessorsAPITests(unittest.TestCase):

    def test_api(self):
        "ProcessorsAPI instance should remember its port"

        self.assertEqual(api.port, port, "Port was not {}".format(port))

    def test_annotate(self):
        "api.annotate should produce a Document when given text"

        text = "This is sentence 1.  This is sentence 2."
        # .annotate should be successful
        doc = api.annotate(text)
        self.assertNotEqual(doc, None, ".annotate failed to produce a Document")
        # should have two sentences
        num_sentences = 2
        self.assertEqual(len(doc.sentences), num_sentences, ".annotate did not produce a Document with {} Sentences for text \"{}\"".format(num_sentences, text))

    def test_fastnlp(self):
        "api.fastnlp.annotate should produce a Document when given text"

        text = "This is sentence 1.  This is sentence 2."
        # .annotate should be successful
        doc = api.fastnlp.annotate(text)
        self.assertNotEqual(doc, None, "fastnlp.annotate failed to produce a Document")
        # should have two sentences
        num_sentences = 2
        self.assertEqual(len(doc.sentences), num_sentences, "fastnlp.annotate did not produce a Document with {} Sentences for text \"{}\"".format(num_sentences, text))

    def test_bionlp(self):
        "api.bionlp.annotate should produce a Document when given text"

        text = "Ras phosphorylated Mek."
        # .annotate should be successful
        doc = api.bionlp.annotate(text)
        self.assertNotEqual(doc, None, "bionlp.annotate failed to produce a Document")
        # should have two sentences
        num_sentences = 1
        self.assertEqual(len(doc.sentences), num_sentences, "bionlp.annotate did not produce a Document with {} Sentences for text \"{}\"".format(num_sentences, text))

    def test_shutdown(self):
        "api.stop_server() should stop processors-server.jar"

        self.assertTrue(api.stop_server(), "Failed to shut down processors-server.jar")

if __name__ == "__main__":
    unittest.main()
