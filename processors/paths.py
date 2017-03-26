#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from processors.utils import LabelManager
import networkx as nx
import collections


class DependencyUtils(object):

    UNKNOWN = LabelManager.UNKNOWN

    @staticmethod
    def build_graph(roots, edges, name):
        """
        Converts a `processors` dependency graph into a networkx graph
        """
        G = nx.Graph()
        graph_name = name
        # store roots
        G.graph["roots"] = roots
        edges = [(edge.source, edge.destination, {"relation": edge.relation}) for edge in edges]
        G.add_edges_from(edges)
        return G

    @staticmethod
    def shortest_path(g, start, end):
        """
        Find the shortest path between two nodes.
        """
        start = start if isinstance(start, collections.Iterable) else [start]
        end = end if isinstance(end, collections.Iterable) else [end]
        # node list -> edges (i.e., (source, dest) pairs)
        def path_to_edges(g, path):
            return [(path[i], path[i+1]) for i in range(len(path) - 1)]

        shortest_paths = []
        for s in start:
            for e in end:
                try:
                    path = nx.algorithms.shortest_path(g, s, e)
                    shortest_paths.append(path_to_edges(g, path))
                # no path found...
                except:
                    #print("No path found between '{}' and '{}'".format(s, e))
                    continue
        return None if len(shortest_paths) == 0 else min(shortest_paths, key=lambda x: len(x))

    @staticmethod
    def retrieve_edges(dep_graph, path):
        shortest_path = []
        for (s, d) in path:
            # build dictionaries from incoming/outgoing
            outgoing = dep_graph.outgoing[s]
            outgoing = dict(outgoing) if len(outgoing) > 0 else dict()
            incoming = dep_graph.incoming[s]
            incoming = dict(incoming) if len(incoming) > 0 else dict()
            relation = ">{}".format(outgoing[d]) if d in outgoing else "<{}".format(incoming[d])
            shortest_path.append((s, relation, d))
        return shortest_path

    @staticmethod
    def simplify_tag(tag):
        simple_tag = "\"{}\"".format(tag)
        # collapse plurals
        if tag.startswith("NNP"):
            simple_tag = "/^NNP/"
        # collapse plurals
        elif tag.startswith("NN"):
            simple_tag = "/^N/"
        elif tag.startswith("VB"):
            simple_tag = "/^V/"
        # collapse comparative, superlatives, etc.
        elif tag.startswith("JJ"):
            simple_tag = "/^J/"
        # collapse comparative, superlatives, etc.
        elif tag.startswith("RB"):
            simple_tag = "/^RB/"
        # collapse possessive/non-possesive pronouns
        elif tag.startswith("PRP"):
            simple_tag = "/^PRP/"
        # treat WH determiners as DT
        elif tag == "WDT":
            simple_tag = "/DT$/"
        # treat DT the same as WDT
        elif tag == "DT":
            simple_tag = "/DT$/"
        return simple_tag

    @staticmethod
    def lexicalize_path(sentence,
                        path,
                        words=False,
                        lemmas=False,
                        tags=False,
                        simple_tags=False,
                        entities=False):

        UNKNOWN = LabelManager.UNKNOWN
        lexicalized_path = []
        relations = []
        nodes = []
        # gather edges and nodes
        for edge in path:
            relations.append(edge[1])
            nodes.append(edge[0])
        nodes.append(path[-1][-1])

        for (i, node) in enumerate(nodes):
            # build token constraints
            token_constraints = []
            # words
            if words:
                token_constraints.append("word=\"{}\"".format(sentence.words[node]))
            # PoS tags
            if tags and sentence.tags[node] != UNKNOWN:
                token_constraints.append("tag=\"{}\"".format(sentence.tags[node]))
            # lemmas
            if lemmas and sentence.lemmas[node] != UNKNOWN:
                token_constraints.append("lemma=\"{}\"".format(sentence.lemmas[node]))
            # NE labels
            if entities and sentence._entities[node] != UNKNOWN:
                token_constraints.append("entity=\"{}\"".format(sentence.entity[node]))
            # simple tags
            if simple_tags and sentence.tags[node] != UNKNOWN:
                token_constraints.append("tag={}".format(DependencyUtils.simplify_tag(sentence.tags[node])))
            # build node pattern
            if len(token_constraints) > 0:
                node_pattern = "[{}]".format(" & ".join(token_constraints))
                # store lexicalized representation of node
                lexicalized_path.append(node_pattern)
            # append next edge
            if i < len(relations):
                lexicalized_path.append(relations[i])
        return " ".join(lexicalized_path)

    @staticmethod
    def pagerank(networkx_graph,
                 alpha=0.85,
                 personalization=None,
                 max_iter=1000,
                 tol=1e-06,
                 nstart=None,
                 weight='weight',
                 dangling=None):
        """
        networkx implementation of pagerank algorithm.
        Use with DirectedGraph.graph.
        """
        return nx.algorithms.link_analysis.pagerank(G=networkx_graph, alpha=alpha, personalization=personalization, max_iter=max_iter, tol=tol, nstart=nstart, weight=weight, dangling=dangling)
