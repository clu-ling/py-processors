#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .utils import post_json
from .ds import Document, Interval
import re
import json


class Mention(object):
    """
    A labeled span of text.  Used to model textual mentions of events, relations, and entities.

    Parameters
    ----------
    token_interval : Interval
        The span of the Mention represented as an Interval.
    sentence : int
        The sentence index that contains the Mention.
    document : Document
        The Document in which the Mention was found.
    foundBy : str
        The Odin IE rule that produced this Mention.
    label : str
        The label most closely associated with this span.  Usually the lowest hyponym of "labels".
    labels: list
        The list of labels associated with this span.
    trigger: dict or None
        dict of JSON for Mention's trigger (event predicate or word(s) signaling the Mention).
    arguments: dict or None
        dict of JSON for Mention's arguments.
    paths: dict or None
        dict of JSON encoding the syntactic paths linking a Mention's arguments to its trigger (applies to Mentions produces from `type:"dependency"` rules).
    doc_id: str or None
        the id of the document

    Attributes
    ----------
    tokenInterval: processors.ds.Interval
        An `Interval` encoding the `start` and `end` of the `Mention`.
    start : int
        The token index that starts the `Mention`.
    end : int
        The token index that marks the end of the Mention (exclusive).
    sentenceObj : processors.ds.Sentence
        Pointer to the `Sentence` instance containing the `Mention`.
    characterStartOffset: int
        The index of the character that starts the `Mention`.
    characterEndOffset: int
        The index of the character that ends the `Mention`.
    type: Mention.TBM or Mention.EM or Mention.RM
        The type of the `Mention`.

    See Also
    --------

    [`Odin` manual](https://arxiv.org/abs/1509.07513)

    Methods
    -------
    matches(label_pattern)
        Test if the provided pattern, `label_pattern`, matches any element in `Mention.labels`.

    """

    TBM = "TextBoundMention"
    EM = "EventMention"
    RM = "RelationMention"

    def __init__(self,
                token_interval,
                sentence,
                document,
                foundBy,
                label,
                labels=None,
                trigger=None,
                arguments=None,
                paths=None,
                keep=True,
                doc_id=None):

        self.label = label
        self.labels = labels if labels else [self.label]
        self.tokenInterval = token_interval
        self.start = self.tokenInterval.start
        self.end = self.tokenInterval.end
        self.document = document
        self._doc_id = doc_id or hash(self.document)
        self.sentence = sentence
        if trigger:
            # NOTE: doc id is not stored for trigger's json,
            # as it is assumed to be contained in the same document as its parent
            trigger.update({"document": self._doc_id})
            self.trigger = Mention.load_from_JSON(trigger, self._to_document_map())
        else:
            self.trigger = None
        # unpack args
        self.arguments = {role:[Mention.load_from_JSON(a, self._to_document_map()) for a in args] for (role, args) in arguments.items()} if arguments else None
        self.paths = paths
        self.keep = keep
        self.foundBy = foundBy
        # other
        self.sentenceObj = self.document.sentences[self.sentence]
        self.text = " ".join(self.sentenceObj.words[self.start:self.end])
        # recover offsets
        self.characterStartOffset = self.sentenceObj.startOffsets[self.tokenInterval.start]
        self.characterEndOffset = self.sentenceObj.endOffsets[self.tokenInterval.end - 1]
        # for later recovery
        self.id = None
        self.type = self._set_type()

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
        m["id"] = self.id
        m["type"] = self.type
        m["label"] = self.label
        m["labels"] = self.labels
        m["tokenInterval"] = self.tokenInterval.to_JSON_dict()
        m["characterStartOffset"] = self.characterStartOffset
        m["characterEndOffset"] = self.characterEndOffset
        m["sentence"] = self.sentence
        m["document"] = self._doc_id
        # do we have a trigger?
        if self.trigger:
             m["trigger"] = self.trigger.to_JSON_dict()
        # do we have arguments?
        if self.arguments:
            m["arguments"] = self._arguments_to_JSON_dict()
        # handle paths
        if self.paths:
            m["paths"] = self.paths
        m["keep"] = self.keep
        m["foundBy"] = self.foundBy
        return m

    def matches(self, label_pattern):
        """
        Test if the provided pattern, `label_pattern`, matches any element in `Mention.labels`.

        Parameters
        ----------
        label_pattern : str or _sre.SRE_Pattern
            The pattern to match against each element in `Mention.labels`

        Returns
        -------
        bool
            True if `label_pattern` matches any element in `Mention.labels`
        """
        return any(label_pattern.match(label) for label in self.labels)

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)

    def _arguments_to_JSON_dict(self):
        return dict((role, [a.to_JSON_dict() for a in args]) for (role, args) in self.arguments.items())

    def _paths_to_JSON_dict(self):
        return {role: paths.to_JSON_dict() for (role, paths) in self.paths}

    @staticmethod
    def load_from_JSON(mjson, docs_dict):
        # recover document
        doc_id = mjson["document"]
        doc = docs_dict[doc_id]
        labels = mjson["labels"]
        kwargs = {
            "label": mjson.get("label", labels[0]),
            "labels": labels,
            "token_interval": Interval.load_from_JSON(mjson["tokenInterval"]),
            "sentence": mjson["sentence"],
            "document": doc,
            "doc_id": doc_id,
            "trigger": mjson.get("trigger", None),
            "arguments": mjson.get("arguments", None),
            "paths": mjson.get("paths", None),
            "keep": mjson.get("keep", True),
            "foundBy": mjson["foundBy"]
        }
        m = Mention(**kwargs)
        # set IDs
        m.id = mjson["id"]
        m._doc_id = doc_id
        # set character offsets
        m.character_start_offset = mjson["characterStartOffset"]
        m.character_end_offset = mjson["characterEndOffset"]
        return m

    def _to_document_map(self):
        return {self._doc_id: self.document}

    def _set_type(self):
        # event mention
        if self.trigger != None:
            return Mention.EM
        # textbound mention
        elif self.trigger == None and self.arguments == None:
            return Mention.TBM
        else:
            return Mention.RM
