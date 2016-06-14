#!/usr/bin/env python
# -*- coding: utf-8 -*-

# use data structures
from .ds import Document, Sentence, Dependencies
import json
import requests


class Processor(object):

    def __init__(self, address):
        self.service = "{}/annotate".format(address)

    def annotate(self, text):
        try:
            # POST json to the server API
            #response = requests.post(self.address, json={"text":"{}".format(text)})
            # for older versions of requests, use the call below
            #print("SERVICE: {}".format(self.service))
            response = requests.post(self.service,
                                     data=json.dumps({"text":"{}".format(text)}),
                                     headers={"content-type": "application/json"},
                                     timeout=None)
            # response content should be utf-8
            content = response.content.decode("utf-8")
            #print("CONTENT: {}".format(content))
            # load json and build Sentences and Document
            annotated_text = json.loads(content)
            parsed_sentences = annotated_text['sentences']
            sentences = []
            for i in parsed_sentences:
                s = parsed_sentences[i]
                words = s['words']
                lemmas = s['lemmas']
                tags = s['tags']
                entities = s['entities']
                deps = Dependencies(s['dependencies'], words)
                sentences.append(Sentence(words=words, lemmas=lemmas, tags=tags, entities=entities, dependencies=deps))
            return Document(text=text, sentences=sentences)
        except Exception as e:
            #print(e)
            print("Error encountered...")
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
