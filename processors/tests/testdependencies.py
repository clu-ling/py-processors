#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from processors import *
import os


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

'''
Testing utilities for manipulating syntactic dependencies.
'''

class DependenciesTests(unittest.TestCase):

    def test_bag_of_labeled(self):
        json_file = os.path.join(__location__,'serialized_biodoc.json')
        with open(json_file) as jf:
            biodoc = Document.load_from_JSON(json.load(jf))
        s = biodoc.sentences[0]
        words_labeled = set([('arthropod', 'det', 'the'), ('arthropod', 'dep', 'cord'), ('arrays', 'amod', 'repeated'), ('cord', 'amod', 'ventral'), ('cord', 'nn', 'nerve'), ('features', 'nsubj', 'arthropod'), ('features', 'dobj', 'number'), ('features', 'vmod', 'occurring'), ('low', 'advmod', 'comparably'), ('number', 'det', 'a'), ('number', 'amod', 'low'), ('number', 'prep_of', 'neurons'), ('neurons', 'amod', 'serotonin-immunoreactive'), ('occurring', 'prep', 'in'), ('occurring', 'dobj', 'arrays'), ('in', 'pcomp', 'segmentally')])
        self.assertEqual(set(s.bag_of_labeled_dependencies_using("words")), words_labeled, "labeled dependencies for sentence using form 'word' were ill-formed.")
        tags_labeled = set([('NN', 'det', 'DT'), ('NN', 'dep', 'NN'), ('NNS', 'amod', 'VBN'), ('NN', 'amod', 'JJ'), ('NN', 'nn', 'NN'), ('VBZ', 'nsubj', 'NN'), ('VBZ', 'dobj', 'NN'), ('VBZ', 'vmod', 'VBG'), ('JJ', 'advmod', 'RB'), ('NN', 'det', 'DT'), ('NN', 'amod', 'JJ'), ('NN', 'prep_of', 'NNS'), ('NNS', 'amod', 'JJ'), ('VBG', 'prep', 'IN'), ('VBG', 'dobj', 'NNS'), ('IN', 'pcomp', 'RB')])
        self.assertEqual(set(s.bag_of_labeled_dependencies_using("tags")), tags_labeled, "labeled dependencies for sentence using form 'tags' were ill-formed.")
        lemmas_labeled = set([('arthropod', 'det', 'the'), ('arthropod', 'dep', 'cord'), ('array', 'amod', 'repeat'), ('cord', 'amod', 'ventral'), ('cord', 'nn', 'nerve'), ('feature', 'nsubj', 'arthropod'), ('feature', 'dobj', 'number'), ('feature', 'vmod', 'occur'), ('low', 'advmod', 'comparably'), ('number', 'det', 'a'), ('number', 'amod', 'low'), ('number', 'prep_of', 'neuron'), ('neuron', 'amod', 'serotonin-immunoreactive'), ('occur', 'prep', 'in'), ('occur', 'dobj', 'array'), ('in', 'pcomp', 'segmentally')])
        self.assertEqual(set(s.bag_of_labeled_dependencies_using("lemmas")),lemmas_labeled, "labeled dependencies for sentence using form 'lemmas' were ill-formed.")
        indices_labeled = set([(1, 'det', 0), (1, 'dep', 4), (18, 'amod', 17), (4, 'amod', 2), (4, 'nn', 3), (5, 'nsubj', 1), (5, 'dobj', 9), (5, 'vmod', 14), (8, 'advmod', 7), (9, 'det', 6), (9, 'amod', 8), (9, 'prep_of', 12), (12, 'amod', 11), (14, 'prep', 15), (14, 'dobj', 18), (15, 'pcomp', 16)])
        self.assertEqual(set(s.bag_of_labeled_dependencies_using("index")), indices_labeled, "labeled dependencies for sentence using form 'index' were ill-formed.")

    def test_bag_of_unlabeled(self):
        json_file = os.path.join(__location__,'serialized_biodoc.json')
        with open(json_file) as jf:
            biodoc = Document.load_from_JSON(json.load(jf))
        s = biodoc.sentences[0]
        words_unlabeled = set([('arthropod', 'the'), ('arthropod', 'cord'), ('arrays', 'repeated'), ('cord', 'ventral'), ('cord', 'nerve'), ('features', 'arthropod'), ('features', 'number'), ('features', 'occurring'), ('low', 'comparably'), ('number', 'a'), ('number', 'low'), ('number', 'neurons'), ('neurons', 'serotonin-immunoreactive'), ('occurring', 'in'), ('occurring', 'arrays'), ('in', 'segmentally')])
        self.assertEqual(set(s.bag_of_unlabeled_dependencies_using("words")), words_unlabeled, "unlabeled dependencies for sentence using form 'word' were ill-formed.")
        tags_unlabeled = set([('NN', 'DT'), ('NN', 'NN'), ('NNS', 'VBN'), ('NN', 'JJ'), ('NN', 'NN'), ('VBZ', 'NN'), ('VBZ', 'NN'), ('VBZ', 'VBG'), ('JJ', 'RB'), ('NN', 'DT'), ('NN', 'JJ'), ('NN', 'NNS'), ('NNS', 'JJ'), ('VBG', 'IN'), ('VBG', 'NNS'), ('IN', 'RB')])
        self.assertEqual(set(s.bag_of_unlabeled_dependencies_using("tags")), tags_unlabeled, "unlabeled dependencies for sentence using form 'tags' were ill-formed.")
        lemmas_unlabeled = set([('arthropod', 'the'), ('arthropod', 'cord'), ('array', 'repeat'), ('cord', 'ventral'), ('cord', 'nerve'), ('feature', 'arthropod'), ('feature', 'number'), ('feature', 'occur'), ('low', 'comparably'), ('number', 'a'), ('number', 'low'), ('number', 'neuron'), ('neuron', 'serotonin-immunoreactive'), ('occur', 'in'), ('occur', 'array'), ('in', 'segmentally')])
        self.assertEqual(set(s.bag_of_unlabeled_dependencies_using("lemmas")),lemmas_unlabeled, "unlabeled dependencies for sentence using form 'lemmas' were ill-formed.")
        indices_unlabeled = set([(1, 0), (1, 4), (18, 17), (4, 2), (4, 3), (5, 1), (5, 9), (5, 14), (8, 7), (9, 6), (9, 8), (9, 12), (12, 11), (14, 15), (14, 18), (15, 16)])
        self.assertEqual(set(s.bag_of_unlabeled_dependencies_using("index")), indices_unlabeled, "unlabeled dependencies for sentence using form 'index' were ill-formed.")

if __name__ == "__main__":
    unittest.main()
