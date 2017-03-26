#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from processors.utils import post_json
from processors.ds import Sentence, Document
from processors.annotators import Message, SegmentedMessage
import json
import six


class SentimentAnalysisAPI(object):
    """
    API for performing sentiment analysis

    Parameters
    ----------
    address : str
        The base address for the API (i.e., everything preceding `/api/..`)

    Attributes
    ----------
    corenlp : processors.sentiment.CoreNLPSentimentAnalyzer
        Service using [`CoreNLP`'s tree-based system](https://nlp.stanford.edu/~socherr/EMNLP2013_RNTN.pdf) for performing sentiment analysis.

    """
    def __init__(self, address):
        self._service = address
        self.corenlp = CoreNLPSentimentAnalyzer(self._service)


class SentimentAnalyzer(object):

    def __init__(self, address):
        self._service = "{}/api/sentiment/score".format(address)
        self._text_service = self._service
        self._segmented_service = self._service
        self._sentence_service = self._service
        self._document_service = self._service

    def score_document(self, doc):
        """
        Sends a Document to the server for sentiment scoring.

        Parameters
        ----------
        doc : processors.ds.Document
            The `doc` to be scored

        Returns
        -------
        [int]
            A list of int scores (one for each sentence) ranging from 1 (very negative) to 5 (very positive)

        """
        try:
            sentiment_scores = post_json(self._document_service, doc.to_JSON())
            return sentiment_scores["scores"]

        except Exception as e:
            #print(e)
            return None

    def score_sentence(self, sentence):
        """
        Sends a Sentence to the server for sentiment scoring.

        Parameters
        ----------
        sentence : processors.ds.Sentence
            The `sentence` to be scored

        Returns
        -------
        int
            A single score ranging from 1 (very negative) to 5 (very positive)

        """
        try:
            sentiment_scores = post_json(self._sentence_service, sentence.to_JSON())
            return sentiment_scores["scores"][0]

        except Exception as e:
            print(e)
            return None

    def score_segmented_text(self, sentences):
        """
        Sends segmented text to the server for sentiment scoring.

        Parameters
        ----------
        sentences : [str]
            A list of str representing segmented sentences/chunks to be scored.

        Returns
        -------
        [int]
            A list of int scores (one for each sentence/chunk) ranging from 1 (very negative) to 5 (very positive)

        """
        try:
            msg = SegmentedMessage(sentences)
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
        Sniff out data type and assemble corresponding message to send to the server for sentiment scoring

        Parameters
        ----------
        data : str or [str] or processors.ds.Sentence or processors.ds.Document
            The data to be scored for sentiment polarity.
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
    Bridge to [`CoreNLP`'s tree-based sentiment analysis system](https://nlp.stanford.edu/~socherr/EMNLP2013_RNTN.pdf)
    """
    def __init__(self, address):
        self._service = "{}/api/sentiment/corenlp/score".format(address)
        self._text_service = self._service
        self._segmented_service = self._service
        self._sentence_service = self._service
        self._document_service = self._service
