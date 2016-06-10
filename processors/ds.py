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
        self._entities = list(chain(*[s._entities for s in self.sentences]))
        self.nes = merge_entity_dicts = self._merge_ne_dicts()
        self.bag_of_labeled_deps = list(chain(*[s.dependencies.labeled for s in self.sentences]))
        self.bag_of_unlabeled_deps = list(chain(*[s.dependencies.unlabeled for s in self.sentences]))
        self.text = text if text else " ".join(self.words)

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

    def __str__(self):
        return self.text

    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

    @staticmethod
    def load_from_JSON(json_dict):
        sentences = []
        for s in json_dict["sentences"]:
            sent = Sentence(
                s["words"],
                s.get("tags", None),
                s.get("lemmas", None),
                s.get("_entities", None),
                s.get("text", None),
                Dependencies.load_from_JSON(s.get("dependencies", dict()))
            )
            sentences.append(sent)
        return Document(sentences, json_dict.get("text", None))

class Sentence(object):

    UNKNOWN = "UNKNOWN"
    # the O in IOB notation
    NONENTITY = "O"

    def __init__(self, words, tags=None, lemmas=None, entities=None, text=None, dependencies=None):
        self.words = words
        self.length = len(self.words)
        self.tags = self._set_toks(tags)
        self.lemmas = self._set_toks(lemmas)
        self._entities = self._set_toks(entities)
        self.text = text if text else " ".join(self.words)
        self.dependencies = dependencies
        self.nes = self._set_nes(entities)

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

    def __str__(self):
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

    @staticmethod
    def load_from_JSON(deps_dict):
        """
        Loads Dependencies from JSON
        """
        deps = Dependencies([], [])
        deps.words = deps_dict.get("_words", [])
        deps.deps = deps_dict.get("deps", [])
        deps.incoming = deps_dict.get("incoming", [])
        deps.outgoing = deps_dict.get("outgoing", [])
        deps.labeled = deps_dict.get("labeled", [])
        deps.unlabeled = deps_dict.get("unlabeled", [])
        return deps
