#!/usr/bin/env python
# -*- coding: utf-8 -*-

# use data structures
from .ds import Document, Sentence, Dependencies
from .utils import post_json
import json


class Processor(object):

    def __init__(self, address):
        self.service = "{}/annotate".format(address)

    def annotate(self, text):
        try:
            # load json and build Sentences and Document
            annotated_text = post_json(self.service, json.dumps({"text":"{}".format(text)}))
            return Document.load_from_JSON(annotated_text)

        except Exception as e:
            #print(e)
            return None
            #raise Exception("Connection refused!  Is the server running?")

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
