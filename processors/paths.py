#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import networkx as nx
import collections


def build_graph(dep_graph):
    """
    Converts a `processors` dependency graph into a networkx graph

    example dep_graph: dg = {'stanford-collapsed': {'roots': [4], 'edges': [{'destination': 0, 'relation': 'nsubj', 'source': 4}, {'destination': 1, 'relation': 'cop', 'source': 4}, {'destination': 2, 'relation': 'det', 'source': 4}, {'destination': 3, 'relation': 'nn', 'source': 4}, {'destination': 6, 'relation': 'rcmod', 'source': 4}, {'destination': 12, 'relation': 'rcmod', 'source': 4}, {'destination': 5, 'relation': 'nsubj', 'source': 6}, {'destination': 10, 'relation': 'dobj', 'source': 6}, {'destination': 12, 'relation': 'conj_and', 'source': 6}, {'destination': 7, 'relation': 'det', 'source': 10}, {'destination': 8, 'relation': 'nn', 'source': 10}, {'destination': 9, 'relation': 'nn', 'source': 10}, {'destination': 5, 'relation': 'nsubj', 'source': 12}, {'destination': 13, 'relation': 'dobj', 'source': 12}]}}
    """
  G = nx.DiGraph()
  # graph has a single key
  graph_name = list(dep_graph.keys())[0]
  # store roots
  G.graph["roots"] = list(dep_graph.values())[0]["roots"]
  edges = [(edge["source"], edge["destination"], {"relation": edge["relation"]})   for edge in   list(dep_graph.values())[0]["edges"]]
  G.add_edges_from(edges)
  return G


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
