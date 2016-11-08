#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from .ds import Document
from .odin import Mention
import json


class JSONSerializer(object):

    @staticmethod
    def mentions_to_JSON_dict(mentions):
        jdict = dict()
        docs = {m._doc_id:m.document.to_JSON_dict() for m in mentions}
        mns = {m.id:m.to_JSON_dict() for m in mentions}
        jdict["documents"] = docs
        jdict["mentions"] = mns
        return jdict

    @staticmethod
    def mentions_to_JSON(mentions):
        return json.dumps(JSONSerializer.mentions_to_JSON_dict(mentions), sort_keys=True, indent=4)

    @staticmethod
    def mentions_from_JSON(jdict):
        # build map of documents
        docs_dict = {doc_id:Document.load_from_JSON(djson) for (doc_id, djson) in jdict["documents"].items()}
        # deserialize mentions
        mns_json = jdict["mentions"]
        mentions = []
        for mjson in mns_json:
            m = Mention.load_from_JSON(mjson, docs_dict)
            mentions.append(m)
        return mentions
