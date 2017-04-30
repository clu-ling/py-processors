#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from processors.utils import LabelManager
from collections import Counter
import networkx as nx
import collections


class DependencyUtils(object):
    """
    A set of utilities for analyzing syntactic dependency graphs.

    Methods
    -------
    build_networkx_graph(roots, edges, name)
        Constructs a networkx.Graph

    shortest_path(g, start, end)
        Finds the shortest path in a `networkx.Graph` between any element in a list of start nodes and any element in a list of end nodes.

    retrieve_edges(dep_graph, path)
        Converts output of `shortest_path` into a list of triples that include the grammatical relation (and direction) for each node-node "hop" in the syntactic dependency graph.

    simplify_tag(tag)
        Maps part of speech (PoS) tag to a subset of PoS tags to better consolidate categorical labels.

    lexicalize_path(sentence, path, words=False, lemmas=False, tags=False, simple_tags=False, entities=False)
        Lexicalizes path in syntactic dependency graph using Odin-style token constraints.

    pagerank(networkx_graph, alpha=0.85, personalization=None, max_iter=1000, tol=1e-06, nstart=None, weight='weight', dangling=None)
        Measures node activity in a `networkx.Graph` using a thin wrapper around `networkx` implementation of pagerank algorithm (see `networkx.algorithms.link_analysis.pagerank`).  Use with `processors.ds.DirectedGraph.graph`.
    """

    UNKNOWN = LabelManager.UNKNOWN

    @staticmethod
    def build_networkx_graph(roots, edges, name, reverse=False):
        """
        Converts a `processors` dependency graph into a networkx graph
        """
        G = nx.DiGraph()
        graph_name = name
        # store roots
        G.graph["roots"] = roots
        # reversing the graph is useful if you want to run pagerank to highlight predicate and argument nodes
        if reverse:
            edges = [(edge.destination, edge.source, {"relation": edge.relation}) for edge in edges]
        else:
            edges = [(edge.source, edge.destination, {"relation": edge.relation}) for edge in edges]
        G.add_edges_from(edges)
        return G

    @staticmethod
    def shortest_paths(g, start, end):
        """
        Find the shortest paths between two nodes.
        Note that if `g` is a directed graph, a path will not be found.

        Parameters
        ----------
        g : a networkx graph
            The networkx graph to explore.

        start : int or [int]
            A single token index or list of token indices serving as the start of the graph traversal.

        end : int or [int]
            A single token index or list of token indices serving as the end of the graph traversal.

        Returns
        -------
        None or [[(int, int)]]
            None if no paths are found.  Otherwise, a list of lists of (source index, target index) tuples representing path segments.
        """
        # converts single int to [int]
        start = start if isinstance(start, collections.Iterable) else [start]
        end = end if isinstance(end, collections.Iterable) else [end]
        # node list -> edges (i.e., (source, dest) pairs)
        def path_to_edges(g, path):
            return [(path[i], path[i+1]) for i in range(len(path) - 1)]

        shortest_paths = []
        # pathfinding b/w pairs of nodes
        for s in start:
            for e in end:
                try:
                    paths = nx.algorithms.all_shortest_paths(g, s, e)
                    for path in paths:
                        shortest_paths.append(path_to_edges(g, path))
                # no path found...
                except:
                    #print("No path found between '{}' and '{}'".format(s, e))
                    continue
        return None if len(shortest_paths) == 0 else shortest_paths

    @staticmethod
    def shortest_path(g, start, end, scoring_func=lambda path: -len(path)):
        """
        Find the shortest path between two nodes.
        Note that pathfinding is sensitive to direction.  If you want to ignore direction, convert your networkx.Digraph to a networkx.Graph.

        Parameters
        ----------
        g : a networkx graph
            The networkx graph to explore.

        start : int or [int]
            A single token index or list of token indices serving as the start of the graph traversal.

        end : int or [int]
            A single token index or list of token indices serving as the end of the graph traversal.

        scoring_func : function
            A function that scores each path in a list of paths.  Each path has the form [(source index, relation, destination index)].
            The path with the maximum score will be returned.

        Returns
        -------
        None or [(int, int)]
            None if no paths are found.  Otherwise, a list of (source index, target index) tuples representing path segments.
        """
        paths = DependencyUtils.shortest_paths(g, start, end)
        return None if len(shortest_paths) == 0 else max(paths, key=scoring_func)

    @staticmethod
    def directed_relation(source_idx, destination_idx, relation, deps):
        """
        Converts relation to a directed relation (incoming v. outgoing)
        if such a relation links `source_idx` and `destination_idx` in `deps`.

        Parameters
        ----------
        source_idx : int
            The token index for the source node

        destination_idx : int
            The token index for the destination node

        relation : str
            The undirected relation (i.e., the grammatical/semantic relation that connects the two nodes)

        deps : processors.ds.DirectedGraph
            The directed graph to be referenced

        Returns
        -------
        str or None
            The directed relation that connects the `source_idx` to the `destination_idx` in `deps`.
        """
        matches = [">{}".format(rel) for d, rel in deps.outgoing[source_idx] if d == destination_idx and rel == relation] + \
        ["<{}".format(rel) for d, rel in deps.incoming[source_idx] if d == destination_idx and rel == relation]
        return None if len(matches) == 0 else matches[0]

    @staticmethod
    def retrieve_edges(dep_graph, path):
        """
        Converts output of `DependencyUtils.shortest_path`
        into a list of triples that include the grammatical relation (and direction)
        for each node-node "hop" in the syntactic dependency graph.

        Parameters
        ----------
        dep_graph : processors.ds.DirectedGraph
            The `DirectedGraph` used to retrieve the grammatical relations for each edge in the `path`.

        path : [(int, int)]
            A list of tuples representing the shortest path from A to B in `dep_graph`.

        Returns
        -------
        [(int, str, int)]
            the shortest path (`path`) enhanced with the directed grammatical relations
            (ex. `>nsubj` for `predicate` to `subject` vs. `<nsubj` for `subject` to `predicate`).
        """

        shortest_path = []
        for (s, d) in path:
            # build dictionaries from incoming/outgoing
            outgoing = {dest_idx:">{}".format(rel) for (dest_idx, rel) in dep_graph.outgoing[s]}
            incoming = {source_idx:"<{}".format(rel) for (source_idx, rel) in dep_graph.incoming[s]}
            relation = outgoing[d] if d in outgoing else incoming[d]
            shortest_path.append((s, relation, d))
        return shortest_path

    @staticmethod
    def simplify_tag(tag):
        """
        Maps part of speech (PoS) tag to a subset of PoS tags to better consolidate categorical labels.

        Parameters
        ----------
        tag : str
            The Penn-style PoS tag to be mapped to a simplified form.

        Returns
        -------
        str
            A simplified form of `tag`.  In some cases, the returned form may be identical to `tag`.
        """
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
                        entities=False,
                        limit_to=None,
                        ):
        """
        Lexicalizes path in syntactic dependency graph using Odin-style token constraints.  Operates on output of `DependencyUtils.retrieve_edges`

        Parameters
        ----------
        sentence : processors.ds.Sentence
            The `Sentence` from which the `path` was found.  Used to lexicalize the `path`.

        path : list
            A list of (source index, relation, target index) triples.

        words : bool
            Whether or not to encode nodes in the `path` with a token constraint constructed from `Sentence.words`

        lemmas : bool
            Whether or not to encode nodes in the `path` with a token constraint constructed from `Sentence.lemmas`

        tags : bool
            Whether or not to encode nodes in the `path` with a token constraint constructed from `Sentence.tags`

        simple_tags : bool
            Whether or not to encode nodes in the `path` with a token constraint constructed from `DependencyUtils.simplify_tag` applied to `Sentence.tags`

        entities : bool
            Whether or not to encode nodes in the `path` with a token constraint constructed from `Sentence._entities`

        limit_to : [int] or None
            Selectively apply lexicalization only to the this list of token indices.  None means apply the specified lexicalization to all token indices in the path.
        Returns
        -------
        [str]
            The lexicalized form of `path`, encoded according to the specified parameters.
        """
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
            if not limit_to or node in limit_to:
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
        return lexicalized_path

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
        Measures node activity in a `networkx.Graph` using a thin wrapper around `networkx` implementation of pagerank algorithm (see `networkx.algorithms.link_analysis.pagerank`).  Use with `processors.ds.DirectedGraph.graph`.

        Parameters
        ----------
        networkx_graph : networkx.Graph
            Corresponds to `G` parameter of `networkx.algorithms.link_analysis.pagerank`.

        See Also
        --------
        Method parameters correspond to those of [`networkx.algorithms.link_analysis.pagerank`](https://networkx.github.io/documentation/development/reference/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html#networkx.algorithms.link_analysis.pagerank_alg.pagerank)

        Returns
        -------
        collections.Counter
            A collections.Counter of node -> pagerank weights
        """
        pg_res = nx.algorithms.link_analysis.pagerank(G=networkx_graph, alpha=alpha, personalization=personalization, max_iter=max_iter, tol=tol, nstart=nstart, weight=weight, dangling=dangling)
        return Counter(pg_res)
