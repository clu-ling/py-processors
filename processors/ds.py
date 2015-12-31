#!/usr/bin/env python
# Gus Hahn-Powell 2015
# data structures for storing processors-server output
# based on conventions from the CLU lab's processors library (https://github.com/clulab/processors)

from itertools import chain
from collections import defaultdict
import re

class Document(object):
    def __init__(self, sentences, text=None):
        self.size = len(sentences)
        self.sentences = sentences
        # easily access token attributes from all sentences
        self.words = list(chain(*[s.words for s in self.sentences]))
        self.tags = list(chain(*[s.tags for s in self.sentences]))
        self.lemmas = list(chain(*[s.lemmas for s in self.sentences]))
        self.entities = list(chain(*[s.entities for s in self.sentences]))
        self.bag_of_labeled_deps = list(chain(*[s.dependencies.labeled for s in self.sentences]))
        self.bag_of_unlabeled_deps = list(chain(*[s.dependencies.unlabeled for s in self.sentences]))
        self.text = text if text else " ".join(self.words)

    def __str__(self):
        return self.text

class Sentence(object):

    UNKNOWN = "UNKNOWN"

    def __init__(self, words, tags=None, lemmas=None, entities=None, text=None, dependencies=None):
        self.words = words
        self.length = len(self.words)
        self.tags = self.set_toks(tags)
        self.lemmas = self.set_toks(lemmas)
        self.entities = self.set_toks(entities)
        self.text = text if text else " ".join(self.words)
        self.dependencies = dependencies

    def set_toks(self, toks):
        return toks if toks else [self.UNKNOWN]*self.length

    def __str__(self):
        return self.text

    def to_string(self):
        return ' '.join("{w}__{p}".format(w=self.words[i],p=self.tags[i]) for i in range(self.length))


class Dependencies(object):
    """
    Storage class for Stanford-style dependencies
    """
    def __init__(self, deps, words):
        self._words = [w.lower() for w in words]
        self.deps = self.unpack_deps(deps)
        self.incoming = self._build_incoming(self.deps)
        self.outgoing = self._build_outgoing(self.deps)
        self.labeled = self._build_labeled()
        self.unlabeled = self._build_unlabeled()

    def __str__(self):
        return self.deps

    def unpack_deps(self, deps):
        dependencies = []
        for dep in deps:
            incoming = dep['incoming']
            outgoing = dep['outgoing']
            rel = dep['relation']
            dependencies.append((incoming, outgoing, rel))
        return dependencies

    def _build_incoming(self, deps):
        dep_dict = defaultdict(list)
        for (incoming, outgoing, rel) in deps:
            dep_dict[outgoing].append((incoming, rel))
        return dep_dict

    def _build_outgoing(self, deps):
        dep_dict = defaultdict(list)
        for (incoming, outgoing, rel) in deps:
            dep_dict[incoming].append((outgoing, rel))
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
