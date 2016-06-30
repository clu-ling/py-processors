#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .utils import post_json
from .ds import Document
import re
import json


class OdinAPI(object):
    """
    API for performing sentiment analysis
    """

    validator = re.compile("^(https?|ftp):.+?\.?ya?ml$")

    def __init__(self, address):
        self._service = "{}/odin/extract".format(address)

    def _extract(self, json_data):
        try:
            mentions = [Mention.load_from_JSON(m) for m in post_json(self._service, json_data)]
            return mentions
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def valid_rule_url(url):
        return True if OdinAPI.validator.match(url) else False

    def extract_from_text(self, text, rules):
        """
        Sends text to the server with rules for IE
        Returns a list of Mentions on None
        """
        if OdinAPI.valid_rule_url(rules):
            # this is actually a URL to a yaml file
            url = rules
            container = TextWithURL(text, url)
        else:
            container = TextWithRules(text, rules)
        return self._extract(container.to_JSON())

    def extract_from_document(self, doc, rules):
        """
        Sends a Document to the server with rules for IE
        Returns a list of Mentions or None
        """
        if OdinAPI.valid_rule_url(rules):
            # this is actually a URL to a yaml file
            url = rules
            container = DocumentWithURL(doc, rules)
        else:
            container = DocumentWithRules(doc, rules)
        return self._extract(container.to_JSON())


class TextWithRules(object):

    def __init__(self, text, rules):
        self.text = text
        self.rules = rules

    def to_JSON_dict(self):
        jdict = dict()
        jdict["text"] = self.text
        jdict["rules"] = self.rules
        return jdict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)

class TextWithURL(object):

    def __init__(self, text, url):
        self.text = text
        # TODO: throw exception if url is invalid
        self.url = url

    def to_JSON_dict(self):
        jdict = dict()
        jdict["text"] = self.text
        jdict["url"] = self.url
        return jdict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)

class DocumentWithRules(object):

    def __init__(self, document, rules):
        # TODO: throw exception if isinstance(document, Document) is False
        self.document = document
        self.rules = rules

    def to_JSON_dict(self):
        jdict = dict()
        jdict["document"] = self.document.to_JSON_dict()
        jdict["rules"] = self.rules
        return jdict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)

class DocumentWithURL(object):

    def __init__(self, document, url):
        # TODO: throw exception if isinstance(document, Document) is False
        self.document = document
        # TODO: throw exception if url is invalid
        self.url = url

    def to_JSON_dict(self):
        jdict = dict()
        jdict["document"] = self.document.to_JSON_dict()
        jdict["url"] = self.url
        return jdict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)

class Mention(object):

    def __init__(self,
                label,
                start,
                end,
                sentence,
                document,
                foundBy,
                labels=None,
                trigger=None,
                arguments=None,
                keep=True):

        self.label = label
        self.labels = labels if labels else [self.label]
        self.start = start
        self.end = end
        self.sentence = sentence
        self.document = document
        self.trigger = Mention.load_from_JSON(trigger) if trigger else None
        # unpack args
        self.arguments = {role:[Mention.load_from_JSON(a) for a in args] for role, args in arguments.items()}
        self.keep = keep
        self.foundBy = foundBy
        # other
        self.sentenceObj = self.document.sentences[self.sentence]
        self.text = " ".join(self.sentenceObj.words[self.start:self.end])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.text

    def to_JSON_dict(self):
        m = dict()
        m["label"] = self.label
        m["labels"] = self.labels
        m["start"] = self.start
        m["end"] = self.label
        m["sentence"] = self.sentence
        m["document"] = self.document.to_JSON_dict()
        # do we have a trigger?
        if self.trigger:
             m["trigger"] = self.trigger
        m["arguments"] = self.arguments_to_JSON_dict()
        m["keep"] = self.keep
        m["foundBy"] = self.foundBy
        return m

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)

    def arguments_to_JSON_dict(self):
        return dict((role, [a.to_JSON_dict() for a in args]) for (role, args) in self.arguments)

    @staticmethod
    def load_from_JSON(jdict):
        sentences = []
        kwargs = {
            "label": jdict["label"],
            "labels": jdict["labels"],
            "start": jdict["start"],
            "end": jdict["end"],
            "sentence": jdict["sentence"],
            "document": Document.load_from_JSON(jdict["document"]),
            "trigger": jdict.get("trigger", None),
            "arguments": jdict.get("arguments", dict()),
            "keep": jdict.get("keep", True),
            "foundBy": jdict["foundBy"]
        }
        return Mention(**kwargs)
