#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
from processors import *


port = 8886
# initialize the server
API = ProcessorsAPI(port=port, timeout=180, keep_alive=True)

class ProcessorsAPITests(unittest.TestCase):

    def test_api(self):
        "ProcessorsAPI instance should remember its port"

        self.assertEqual(API.port, port, "Port was not {}".format(port))

    # annotate tests
    def test_annotate(self):
        "API.annotate should produce a Document when given text"

        text = "This is sentence 1.  This is sentence 2."
        # .annotate should be successful
        doc = API.annotate(text)
        self.assertNotEqual(doc, None, ".annotate failed to produce a Document")
        # should have two sentences
        num_sentences = 2
        self.assertEqual(len(doc.sentences), num_sentences, ".annotate did not produce a Document with {} Sentences for text \"{}\"".format(num_sentences, text))

    def test_unicode(self):
        "API.annotate should produce a Document when given text containg unicode"
        # the server will do a poor job with non-English text, but it should still produce something...
        text = "頑張らなきゃならい"
        doc = API.annotate(text)
        self.assertNotEqual(doc, None, ".annotate failed to produce a Document")

    # annotate_from_sentences tests
    def test_annotate_from_sentences(self):
        "API.annotate_from_sentences should produce a Document that preserves the provided sentence segmentation"

        sentences = ["This is sentence 1.", "This is sentence 2."]
        # .annotate should be successful
        doc = API.annotate_from_sentences(sentences)
        self.assertNotEqual(doc, None, ".annotate_from_sentences failed to produce a Document")
        # should have two sentences
        self.assertEqual(len(doc.sentences), len(sentences), ".annotate_from_sentences did not produce a Document with the correct number of sentences")

    def test_fastnlp(self):
        "API.fastnlp.annotate should produce a Document when given text"

        text = "This is sentence 1.  This is sentence 2."
        # .annotate should be successful
        doc = API.fastnlp.annotate(text)
        self.assertNotEqual(doc, None, "fastnlp.annotate failed to produce a Document")
        # should have two sentences
        num_sentences = 2
        self.assertEqual(len(doc.sentences), num_sentences, "fastnlp.annotate did not produce a Document with {} Sentences for text \"{}\"".format(num_sentences, text))

    def test_bionlp(self):
        "API.bionlp.annotate should produce a Document when given text"

        text = "Ras phosphorylated Mek."
        # .annotate should be successful
        doc = API.bionlp.annotate(text)
        self.assertNotEqual(doc, None, "bionlp.annotate failed to produce a Document")
        # should have two sentences
        num_sentences = 1
        self.assertEqual(len(doc.sentences), num_sentences, "bionlp.annotate did not produce a Document with {} Sentences for text \"{}\"".format(num_sentences, text))

    # sentiment analysis tests
    def test_sentiment_analysis_of_text(self):
        "API.sentiment.corenlp.score_text should return scores for text"

        scores = API.sentiment.corenlp.score_text("This is a very sad sentence.")
        self.assertTrue(len(scores) > 0, "there were no sentiment scores returned for the text")

    def test_sentiment_analysis_of_document(self):
        "API.sentiment.corenlp.score_document should return scores for Document"

        text = "This is a terribly sad sentence."
        doc = API.annotate(text)
        scores = API.sentiment.corenlp.score_document(doc)
        self.assertTrue(len(scores) > 0, "there were no sentiment scores returned for the Document")

    def test_sentiment_analysis_of_sentence(self):
        "API.sentiment.corenlp.score_sentence should return a score for a Sentence"

        text = "This is a terribly sad sentence."
        doc = API.annotate(text)
        s = doc.sentences[0]
        score = API.sentiment.corenlp.score_sentence(s)
        self.assertIsInstance(score, int, "score for Sentence should be of type int, but was of type {}".format(type(score)))

    def test_sentiment_analysis_of_segemented_text(self):
        "API.sentiment.corenlp.score_segemented_text should return a score for each sentence its provided"

        sentences = ["This is a terribly sad sentence.", "I'm pretty happy, though :) !"]
        scores = API.sentiment.corenlp.score_segmented_text(sentences)
        self.assertTrue(len(scores) == len(sentences), "there should be {} scores, but only {} were produced :(".format(len(sentences), len(scores)))

    def test_sentiment_analysis_score_method(self):
        "API.sentiment.corenlp.score should be able to determine the appropriate API endpoint for the given parameter"
        # test with text
        text = "This is a terribly sad sentence."
        scores = API.sentiment.corenlp.score(text)
        self.assertTrue(len(scores) > 0, "there were no sentiment scores returned for the text")
        # test with Document
        doc = API.annotate(text)
        scores = API.sentiment.corenlp.score(doc)
        self.assertTrue(len(scores) > 0, "there were no sentiment scores returned for the Document")
        # test with Sentence
        s = doc.sentences[0]
        score = API.sentiment.corenlp.score(s)
        self.assertIsInstance(score, int, "score for Sentence should be of type int, but was of type {}".format(type(score)))

    # Odin tests
    def test_odin_extract_from_text_method(self):
        "API.odin.extract_from_text should return mentions whenever rules match the text"
        rules = """
        - name: "ner-person"
          label: [Person, PossiblePerson, Entity]
          priority: 1
          type: token
          pattern: |
           [entity="PERSON"]+
           |
           [tag=/^N/]* [tag=/^N/ & outgoing="cop"] [tag=/^N/]*
        """
        text = 'Inigo Montoya should be flagged as a Person.'
        mentions = API.odin.extract_from_text(text, rules)
        self.assertTrue(len(mentions) == 1, "More than one mention found for text.")
        m = mentions[0]
        self.assertIsInstance(m, Mention, "m wasn't a Mention")
        self.assertEqual(m.label, "Person", "Label of Mention was not \"Person\"")

    def test_odin_extract_from_text_method2(self):
        "API.odin.extract_from_text should be capable of handling a URL pointing to a yaml (rules) file"
        rules_url = "https://raw.githubusercontent.com/clulab/reach/master/src/main/resources/edu/arizona/sista/demo/open/grammars/rules.yml"
        text = 'Inigo Montoya should be flagged as a Person.'
        mentions = API.odin.extract_from_text(text, rules_url)
        self.assertTrue(len(mentions) != 0, "No mentions were found")
        m = mentions[0]
        self.assertIsInstance(m, Mention, "m wasn't a Mention")
        person_mentions = [m for m in mentions if m.label == "Person"]
        self.assertTrue(len(person_mentions) == 1, "{} \"Person\" Mentions found, but 1 expected.".format(len(person_mentions)))

    def test_odin_extract_from_document_method(self):
        "API.odin.extract_from_document should return mentions whenever rules match the text"
        rules = """
        - name: "ner-person"
          label: [Person, PossiblePerson, Entity]
          priority: 1
          type: token
          pattern: |
           [entity="PERSON"]+
           |
           [tag=/^N/]* [tag=/^N/ & outgoing="cop"] [tag=/^N/]*
        """
        text = 'Inigo Montoya should be flagged as a Person.'
        doc = API.annotate(text)
        mentions = API.odin.extract_from_document(doc, rules)
        self.assertTrue(len(mentions) == 1, "More than one mention found for text.")
        m = mentions[0]
        self.assertIsInstance(m, Mention, "m wasn't a Mention")
        self.assertEqual(m.label, "Person", "Label of Mention was not \"Person\"")

    def test_odin_extract_from_document_method2(self):
        "API.odin.extract_from_document should be capable of handling a URL pointing to a yaml (rules) file"
        rules_url = "https://raw.githubusercontent.com/clulab/reach/master/src/main/resources/edu/arizona/sista/demo/open/grammars/rules.yml"
        text = 'Inigo Montoya should be flagged as a Person.'
        doc = API.annotate(text)
        mentions = API.odin.extract_from_document(doc, rules_url)
        self.assertTrue(len(mentions) != 0, "No mentions were found")
        m = mentions[0]
        self.assertIsInstance(m, Mention,  "m wasn't a Mention")
        person_mentions = [m for m in mentions if m.label == "Person"]
        self.assertTrue(len(person_mentions) == 1, "{} \"Person\" Mentions found, but 1 expected.".format(len(person_mentions)))

    def test_shutdown(self):
        "api.stop_server() should stop processors-server.jar"

        self.assertTrue(API.stop_server(), "Failed to shut down processors-server.jar")

if __name__ == "__main__":
    unittest.main()
