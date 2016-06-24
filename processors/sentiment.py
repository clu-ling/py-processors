#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .utils import post_json
from .ds import Sentence, Document
from .processors import Message, SentencesMessage
import json
import six


class SentimentAnalysisAPI(object):
    """
    API for performing sentiment analysis
    """
    def __init__(self, address):
        self._service = address
        self.corenlp = CoreNLPSentimentAnalyzer(self._service)


class SentimentAnalyzer(object):

    def __init__(self, address):
        self._service = "{}/sentiment/score".format(address)
        self._text_service = self._service
        self._segmented_service = self._service
        self._sentence_service = self._service
        self._document_service = self._service

    def score_document(self, doc):
        """
        Sends a Document to the server for sentiment scoring
        Returns a list of scores (one for each sentence)
        """
        try:
            sentiment_scores = post_json(self._document_service, doc.to_JSON())
            return sentiment_scores["scores"]

        except Exception as e:
            #print(e)
            return None

    def score_sentence(self, sentence):
        """
        Sends a Sentence to the server for sentiment scoring
        Returns a single score
        """
        try:
            sentiment_scores = post_json(self._sentence_service, sentence.to_JSON())
            return sentiment_scores["scores"][0]

        except Exception as e:
            print(e)
            return None

    def score_segmented_text(self, sentences):
        """
        Sends segmented text to the server for sentiment scoring
        Returns a score for each sentence
        """
        try:
            msg = SentencesMessage(sentences)
            sentiment_scores = post_json(self._segmented_service, msg.to_JSON())
            return sentiment_scores["scores"]

        except Exception as e:
            #print(e)
            return None

    def score_text(self, text):
        """
        Sends text to the server for sentiment scoring
        Returns a list of scores (one for each sentence)
        """
        service = self._text_service
        try:
            msg = Message(text)
            sentiment_scores = post_json(self._text_service, msg.to_JSON())
            return sentiment_scores["scores"]

        except Exception as e:
            #print(e)
            return None

    def score(self, data):
        """
        Sniff out data type and to properly send to the server for sentiment scoring
        """
        if isinstance(data, six.text_type):
            return self.score_text(data)
        elif isinstance(data, Sentence):
            return self.score_sentence(data)
        elif isinstance(data, Document):
            return self.score_document(data)
        # a list of pre segmented sentences
        elif isinstance(data, list):
            return self.score_segmented_text(data)
        else:
            #print("Type of data: {}".format(type(data)))
            return None


class CoreNLPSentimentAnalyzer(SentimentAnalyzer):
    """
    Bridge to CoreNLP's tree-based sentiment analysis
    """
    def __init__(self, address):
        self._service = "{}/sentiment/corenlp/score".format(address)
        self._text_service = self._service
        self._segmented_service = "{}/segmented".format(self._service)
        self._sentence_service = self._service
        self._document_service = self._service
