#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Gus Hahn-Powell 2015
# data structures for storing processors-server output
# based on conventions from the CLU lab's processors library (https://github.com/clulab/processors)
from __future__ import unicode_literals
from itertools import chain
from collections import defaultdict
#from six import text_type
import json
import re


class Document(object):

    def __init__(self, sentences, text=None):
        self.size = len(sentences)
        self.sentences = sentences
        # easily access token attributes from all sentences
        self.words = list(chain(*[s.words for s in self.sentences]))
        self.tags = list(chain(*[s.tags for s in self.sentences]))
        self.lemmas = list(chain(*[s.lemmas for s in self.sentences]))
        self._entities = list(chain(*[s._entities for s in self.sentences]))
        self.nes = merge_entity_dicts = self._merge_ne_dicts()
        self.bag_of_labeled_deps = list(chain(*[s.dependencies.labeled for s in self.sentences]))
        self.bag_of_unlabeled_deps = list(chain(*[s.dependencies.unlabeled for s in self.sentences]))
        self.text = text if text else " ".join(self.words)

    def __unicode__(self):
        return self.text

    def __str__(self):
        return "Document w/ {} Sentence{}".format(self.size, "" if self.size == 1 else "s")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def bag_of_labeled_dependencies_using(self, form):
        return list(chain(*[s.labeled_dependencies_using(form) for s in self.sentences]))

    def bag_of_unlabeled_dependencies_using(self, form):
        return list(chain(*[s.unlabeled_dependencies_using(form) for s in self.sentences]))

    def _merge_ne_dicts(self):
        # Get the set of all NE labels found in the Doc's sentences
        entity_labels = set(chain(*[s.nes.keys() for s in self.sentences]))
        # Do we have any labels?
        if entity_labels == None:
            return None
        # If we have labels, consolidate the NEs under the appropriate label
        else:
            nes_dict = dict()
            for e in entity_labels:
                entities = []
                for s in self.sentences:
                    entities += s.nes[e]
                nes_dict[e] = entities
            return nes_dict

    def to_JSON_dict(self):
        doc_dict = dict()
        doc_dict["sentences"] = [s.to_JSON_dict() for s in self.sentences]
        doc_dict["text"] = self.text
        return doc_dict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)

    @staticmethod
    def load_from_JSON(json_dict):
        sentences = []
        for s in json_dict["sentences"]:
            kwargs = {
                "words": s["words"],
                "startOffsets": s["startOffsets"],
                "endOffsets": s["endOffsets"],
                "tags": s.get("tags", None),
                "lemmas": s.get("lemmas", None),
                "entities": s.get("entities", None),
                "text": s.get("text", None),
                "dependencies": s.get("dependencies", None)
            }
            sent = Sentence(**kwargs)
            sentences.append(sent)
        return Document(sentences, json_dict.get("text", None))

class Sentence(object):

    UNKNOWN = "UNKNOWN"
    # the O in IOB notation
    NONENTITY = "O"

    def __init__(self, **kwargs):
        self.words = kwargs["words"]
        self.startOffsets = kwargs["startOffsets"]
        self.endOffsets = kwargs["endOffsets"]
        self.length = len(self.words)
        self.tags = self._set_toks(kwargs.get("tags", None))
        self.lemmas = self._set_toks(kwargs.get("lemmas", None))
        self._entities = self._set_toks(kwargs.get("entities", None))
        self.text = kwargs.get("text", None) or " ".join(self.words)
        self.dependencies = self._build_dependencies_from_dict(kwargs.get("dependencies", None))
        self.nes = self._set_nes(self._entities)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def _set_toks(self, toks):
        return toks if toks else [self.UNKNOWN]*self.length

    def _set_nes(self, entities):
        """
        Consolidates consecutive NEs under the appropriate label
        """
        entity_dict = defaultdict(list)
        # initialize to empty label
        current = Sentence.NONENTITY
        start = None
        end = None
        for i, e in enumerate(entities):
            # we don't have an entity tag
            if e == Sentence.NONENTITY:
                # did we have an entity with the last token?
                if current == Sentence.NONENTITY:
                    continue
                else:
                    # the last sequence has ended
                    end = i
                    # store the entity
                    named_entity = ' '.join(self.words[start:end])
                    entity_dict[current].append(named_entity)
                    # reset our book-keeping vars
                    current = Sentence.NONENTITY
                    start = None
                    end = None
            # we have an entity tag!
            else:
                # our old sequence continues
                if e == current:
                    end = i
                # our old sequence has ended
                else:
                    # do we have a previous NE?
                    if current != Sentence.NONENTITY:
                        end = i
                        named_entity = ' '.join(self.words[start:end])
                        entity_dict[current].append(named_entity)
                    # update our book-keeping vars
                    current = e
                    start = i
                    end = None
        # this might be empty
        return entity_dict

    def _build_dependencies_from_dict(self, deps):
        if deps and len(deps) > 0:
            return Dependencies(deps, self.words)
        return None

    def __unicode__(self):
        return self.text

    def to_string(self):
        return ' '.join("{w}__{p}".format(w=self.words[i],p=self.tags[i]) for i in range(self.length))

    def labeled_dependencies_using(self, form):
        """
        Generates a list of labeled dependencies for a sentence
        using "words", "tags", "lemmas", "entities", or token index ("index")
        """

        f = form.lower()
        if f == "words":
            tokens = self.words
        elif f == "tags":
            tokens = self.tags
        elif f == "lemmas":
            tokens = self.lemmas
        elif f == "entities":
            tokens = self.nes
        elif f == "index":
            tokens = list(range(self.length))
        #else:
        #    raise Exception("""form must be "words", "tags", "lemmas", or "index"""")
        deps = self.dependencies
        labeled = []
        for out in deps.outgoing:
            for (dest, rel) in deps.outgoing[out]:
                labeled.append("{}_{}_{}".format(tokens[out], rel.upper(), tokens[dest]))
        return labeled

    def unlabeled_dependencies_using(self, form):
        """
        Generate a list of unlabeled dependencies for a sentence
        using "words", "tags", "lemmas", "entities", or token index ("index")
        """
        unlabeled = []
        for sd in self.labeled_dependencies_using(form):
            (head, _, dep) = sd.split("_")
            unlabeled.append("{}_{}".format(head, dep))
        return unlabeled

    def to_JSON_dict(self):
        sentence_dict = dict()
        sentence_dict["words"] = self.words
        sentence_dict["startOffsets"] = self.startOffsets
        sentence_dict["endOffsets"] = self.endOffsets
        sentence_dict["tags"] = self.tags
        sentence_dict["lemmas"] = self.lemmas
        sentence_dict["entities"] = self._entities
        sentence_dict["dependencies"] = self.dependencies.to_JSON_dict()
        return sentence_dict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)

    @staticmethod
    def load_from_JSON(json_dict):
        sent = Sentence(
                    words=json_dict["words"],
                    startOffsets=json_dict["startOffsets"],
                    endOffsets=json_dict["endOffsets"],
                    lemmas=json_dict.get("lemmas", None),
                    tags=json_dict.get("tags", None),
                    entities=json_dict.get("entities", None),
                    text=json_dict.get("text", None),
                    dependencies=json_dict.get("dependencies", None)
                    )
        return sent


class Dependencies(object):
    """
    Storage class for Stanford-style dependencies
    """
    def __init__(self, deps, words):
        self._words = [w.lower() for w in words]
        self.deps = self.unpack_deps(deps)
        self.roots = deps.get("roots", [])
        self.edges = deps["edges"]
        self.incoming = self._build_incoming(self.deps)
        self.outgoing = self._build_outgoing(self.deps)
        self.labeled = self._build_labeled()
        self.unlabeled = self._build_unlabeled()

    def __unicode__(self):
        return self.deps

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def unpack_deps(self, deps):
        dependencies = []
        for edge in deps["edges"]:
            outgoing = edge['source']
            incoming = edge['destination']
            rel = edge['relation']
            dependencies.append((incoming, outgoing, rel))
        return dependencies

    def _build_incoming(self, deps):
        dep_dict = defaultdict(list)
        for (incoming, outgoing, rel) in deps:
            dep_dict[incoming].append((outgoing, rel))
        return dep_dict

    def _build_outgoing(self, deps):
        dep_dict = defaultdict(list)
        for (incoming, outgoing, rel) in deps:
            dep_dict[outgoing].append((incoming, rel))
        return dep_dict

    def _build_labeled(self):
        labeled = []
        for out in self.outgoing:
            for (dest, rel) in self.outgoing[out]:
                labeled.append("{}_{}_{}".format(self._words[out], rel.upper(), self._words[dest]))
        return labeled

    def _build_unlabeled(self):
        unlabeled = []
        for out in self.outgoing:
            for (dest, _) in self.outgoing[out]:
                unlabeled.append("{}_{}".format(self._words[out], self._words[dest]))
        return unlabeled

    def to_JSON_dict(self):
        deps_dict = dict()
        deps_dict["edges"] = self.edges
        deps_dict["roots"] = self.roots
        return deps_dict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)
