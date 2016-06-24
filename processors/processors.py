#!/usr/bin/env python
# -*- coding: utf-8 -*-

# use data structures
from __future__ import unicode_literals
from .ds import Document, Sentence, Dependencies
from .utils import post_json
import json


class Processor(object):

    def __init__(self, address):
        self.service = "{}/annotate".format(address)

    def _message_to_json_dict(self, msg):
        return post_json(self.service, msg.to_JSON())

    def _annotate_message(self, msg):
        annotated_text = post_json(self.service, msg.to_JSON())
        return Document.load_from_JSON(annotated_text)

    def annotate(self, text):
        try:
            # load json and build Sentences and Document
            msg = Message(text)
            return self._annotate_message(msg)

        except Exception as e:
            #print(e)
            return None

    def annotate_from_sentences(self, sentences):
        """
        Annotate text that has already been segmented into sentences.
        """
        try:
            # load json from str interable and build Sentences and Document
            msg = SentencesMessage(sentences)
            return self._annotate_message(msg)

        except Exception as e:
            #print(e)
            return None

class FastNLPProcessor(Processor):

    def __init__(self, address):
        self.service = "{}/fastnlp/annotate".format(address)

    def annotate(self, text):
        return super(FastNLPProcessor, self).annotate(text)


class BioNLPProcessor(Processor):

    def __init__(self, address):
        self.service = "{}/bionlp/annotate".format(address)

    def annotate(self, text):
        return super(BioNLPProcessor, self).annotate(text)


class Message(object):
    def __init__(self, text):
        self.text = text

    def to_JSON_dict(self):
        jdict = dict()
        jdict["text"] = self.text
        return jdict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)


class SentencesMessage(object):
    def __init__(self, sentences):
        self.sentences = sentences

    def to_JSON_dict(self):
        jdict = dict()
        jdict["sentences"] = self.sentences
        return jdict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)
