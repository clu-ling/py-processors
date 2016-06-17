#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .utils import post_json
from .ds import Sentence, Document
import json


class SentimentAnalysisAPI(object):
    """
    API for performing sentiment analysis
    """
    def __init__(self, address):
        self._service = address
        self.corenlp = CoreNLPSentimentAnalyzer(self._service)


class SentimentAnalyzer(object):

    def __init__(self, address):
        self._service = "{}/sentiment".format(address)

    def score_document(self, doc):
        """
        Sends a Document to the server for sentiment scoring
        Returns a list of scores (one for each sentence)
        """
        service = "{}/document".format(self._service)
        try:
            sentiment_scores = post_json(service, doc.to_JSON())
            return sentiment_scores["scores"]

        except Exception as e:
            print(e)
            return None
            #raise Exception("Connection refused!  Is the server running?")

    def score_sentence(self, sentence):
        """
        Sends a Sentence to the server for sentiment scoring
        Returns a single score
        """
        service = "{}/sentence".format(self._service)
        try:
            sentiment_scores = post_json(service, sentence.to_JSON())
            return sentiment_scores["scores"][0]

        except Exception as e:
            print(e)
            return None
            #raise Exception("Connection refused!  Is the server running?")

    def score_text(self, text):
        """
        Sends text to the server for sentiment scoring
        Returns a list of scores (one for each sentence)
        """
        service = "{}/text".format(self._service)
        try:
            sentiment_scores = post_json(service, json.dumps({"text":"{}".format(text)}))
            return sentiment_scores["scores"]

        except Exception as e:
            print(e)
            return None
            #raise Exception("Connection refused!  Is the server running?")

    def score(self, data):
        """
        Sniff out data type and to properly send to the server for sentiment scoring
        """
        if isinstance(data, str):
            return self.score_text(data)
        elif isinstance(data, Sentence):
            return self.score_sentence(data)
        elif isinstance(data, Document):
            return self.score_document(data)
        else:
            return None


class CoreNLPSentimentAnalyzer(SentimentAnalyzer):
    """
    Bridge to CoreNLP's tree-based sentiment analysis
    """
    def __init__(self, address):
        self._service = "{}/corenlp/sentiment".format(address)
