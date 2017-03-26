#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Gus Hahn-Powell 2015-2016
# data structures for storing processors-server output
# based on conventions from the CLU lab's processors library (https://github.com/clulab/processors)
from __future__ import unicode_literals
from itertools import chain
from collections import defaultdict
from processors.paths import DependencyUtils
from processors.utils import LabelManager
#from six import text_type
import json
import re


class Document(object):

    def __init__(self, sentences):
        self.id = None
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
        self.text = None

    def __hash__(self):
        return hash(self.to_JSON())

    def __unicode__(self):
        return self.text

    def __str__(self):
        return "Document w/ {} Sentence{}".format(self.size, "" if self.size == 1 else "s")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.to_JSON() == other.to_JSON()
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def bag_of_labeled_dependencies_using(self, form):
        return list(chain(*[s.labeled_dependencies_using(s._get_tokens(form)) for s in self.sentences]))

    def bag_of_unlabeled_dependencies_using(self, form):
        return list(chain(*[s.unlabeled_dependencies_using(s._get_tokens(form)) for s in self.sentences]))

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
        # can the ID be set?
        if self.id != None:
            doc_dict["id"] = self.id
        return doc_dict

    def to_JSON(self, pretty=True):
        """
        Returns JSON as String.
        """
        num_spaces = 4 if pretty else 0
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=num_spaces)

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
                "chunks": s.get("chunks", None),
                "entities": s.get("entities", None),
                "graphs": s.get("graphs", None)
            }
            sent = Sentence(**kwargs)
            sentences.append(sent)
        doc = Document(sentences)
        # set id and text
        doc.text = json_dict.get("text", None)
        doc.id = kwargs.get("id", None)
        return doc


class Sentence(object):

    UNKNOWN = LabelManager.UNKNOWN
    # the O in IOB notation
    O = LabelManager.O

    def __init__(self, **kwargs):
        self.words = kwargs["words"]
        self.startOffsets = kwargs["startOffsets"]
        self.endOffsets = kwargs["endOffsets"]
        self.length = len(self.words)
        self.tags = self._set_toks(kwargs.get("tags", None))
        self.lemmas = self._set_toks(kwargs.get("lemmas", None))
        self._chunks = self._set_toks(kwargs.get("chunks", None))
        self._entities = self._set_toks(kwargs.get("entities", None))
        self.text = kwargs.get("text", None) or " ".join(self.words)
        self.graphs = self._build_direct_graph_from_dict(kwargs.get("graphs", None))
        self.basic_dependencies = self.graphs.get(DirectedGraph.STANFORD_BASIC_DEPENDENCIES, None)
        self.collapsed_dependencies = self.graphs.get(DirectedGraph.STANFORD_COLLAPSED_DEPENDENCIES, None)
        self.dependencies = self.collapsed_dependencies if self.collapsed_dependencies != None else self.basic_dependencies
        # IOB tokens -> {label: [phrase 1, ..., phrase n]}
        self.nes = self._handle_iob(self._entities)
        self.phrases = self._handle_iob(self._chunks)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.to_JSON() == other.to_JSON()
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def _get_tokens(self, form):
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
        return tokens

    def _set_toks(self, toks):
        return toks if toks else [Sentence.UNKNOWN]*self.length

    def _handle_iob(self, iob):
        """
        Consolidates consecutive tokens in IOB notation under the appropriate label.
        Regexs control for bionlp annotator, which uses IOB notation.
        """
        entity_dict = defaultdict(list)
        # initialize to empty label
        current = Sentence.O
        start = None
        end = None
        for i, tok in enumerate(iob):
            # we don't have an I or O
            if tok == Sentence.O:
                # did we have an entity with the last token?
                current = re.sub('(B-|I-)','', str(current))
                if current == Sentence.O:
                    continue
                else:
                    # the last sequence has ended
                    end = i
                    # store the entity
                    named_entity = ' '.join(self.words[start:end])
                    entity_dict[current].append(named_entity)
                    # reset our book-keeping vars
                    current = Sentence.O
                    start = None
                    end = None
            # we have a tag!
            else:
                # our old sequence continues
                current = re.sub('(B-|I-)','', str(current))
                tok = re.sub('(B-|I-)','', str(tok))
                if tok == current:
                    end = i
                # our old sequence has ended
                else:
                    # do we have a previous NE?
                    if current != Sentence.O:
                        end = i
                        named_entity = ' '.join(self.words[start:end])
                        entity_dict[current].append(named_entity)
                    # update our book-keeping vars
                    current = tok
                    start = i
                    end = None
        # this might be empty
        return entity_dict

    def _build_direct_graph_from_dict(self, graphs):
        deps_dict = dict()
        if graphs and len(graphs) > 0:
            # process each stored graph
            for (kind, deps) in graphs.items():
                deps_dict[kind] = DirectedGraph(kind, deps, self.words)
            return deps_dict
        return None

    def __unicode__(self):
        return self.text

    def to_string(self):
        return ' '.join("{w}__{p}".format(w=self.words[i],p=self.tags[i]) for i in range(self.length))

    def labeled_dependencies_using(self, tokens):
        """
        Generates a list of labeled dependencies for a sentence
        using the provided tokens
        """
        #else:
        #    raise Exception("""form must be "words", "tags", "lemmas", or "index"""")
        deps = self.dependencies
        labeled = []
        for out in deps.outgoing:
            for (dest, rel) in deps.outgoing[out]:
                labeled.append("{}_{}_{}".format(tokens[out], rel.upper(), tokens[dest]))
        return labeled

    def unlabeled_dependencies_using(self, tokens):
        """
        Generate a list of unlabeled dependencies for a sentence
        using the provided tokens
        """
        unlabeled = []
        for sd in self.labeled_dependencies_using(tokens):
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
        # add graphs
        sentence_dict["graphs"] = dict()
        for (kind, graph) in self.graphs.items():
            sentence_dict["graphs"][kind] = graph._graph_to_JSON_dict()
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
                    dependencies=json_dict.get("graphs", None)
                    )
        return sent


class Edge(object):

    def __init__(self, source, destination, relation):
        self.source = source
        self.destination = destination
        self.relation = relation

    def __unicode__(self):
        return self.to_string()

    def to_string(self):
        return "Edge(source: {}, destination: {}, relation: {})".format(self.source, self.destination, self.relation)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.to_JSON() == other.to_JSON()
        else:
            return False

    def to_JSON_dict(self):
        edge_dict = dict()
        edge_dict["source"] = self.source
        edge_dict["destination"] = self.destination
        edge_dict["relation"] = self.relation
        return edge_dict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)


class DirectedGraph(object):

    """
    Storage class for directed graphs.
    """
    STANFORD_BASIC_DEPENDENCIES = "stanford-basic"
    STANFORD_COLLAPSED_DEPENDENCIES = "stanford-collapsed"

    def __init__(self, kind, deps, words):
        self._words = [w.lower() for w in words]
        self.kind = kind
        self.roots = deps.get("roots", [])
        self.edges = [Edge(e["source"], e["destination"], e["relation"]) for e in deps["edges"]]
        self.incoming = self._build_incoming(self.edges)
        self.outgoing = self._build_outgoing(self.edges)
        self.labeled = self._build_labeled()
        self.unlabeled = self._build_unlabeled()
        self.graph = DependencyUtils.build_graph(roots=self.roots, edges=self.edges, name=self.kind)

    def __unicode__(self):
        return self.edges

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.to_JSON() == other.to_JSON()
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def shortest_path(self, start, end):
        """
        Find the shortest path in the syntactic depedency graph
        between the provided start and end nodes.
        """
        res = DependencyUtils.shortest_path(self.graph, start, end)
        return DependencyUtils.retrieve_edges(self, res) if res else None

    def _build_incoming(self, edges):
        dep_dict = defaultdict(list)
        for edge in edges:
            dep_dict[edge.destination].append((edge.source, edge.relation))
        return dep_dict

    def _build_outgoing(self, edges):
        dep_dict = defaultdict(list)
        for edge in edges:
            dep_dict[edge.source].append((edge.destination, edge.relation))
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

    def _graph_to_JSON_dict(self):
        dg_dict = dict()
        dg_dict["edges"] = [e.to_JSON_dict() for e in self.edges]
        dg_dict["roots"] = self.roots
        return dg_dict

    def to_JSON_dict(self):
        return {self.kind:self._graph_to_JSON_dict()}

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)


class Interval(object):
    """
    Defines a token or character span

    Parameters
    ----------
    start : str
        The token or character index where the interval begins.
    end : str
        The 1 + the index of the last token/character in the span.
    """

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def to_JSON_dict(self):
        return {"start":self.start, "end":self.end}

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)

    @staticmethod
    def load_from_JSON(json):
        return Interval(start=json["start"], end=json["end"])
