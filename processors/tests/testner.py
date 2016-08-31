#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from processors import *
import os


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

'''
Testing named entity recognition. 
IOB notation should be neutralized for bionlp
'''

class NERTests(unittest.TestCase):

	def test_bio_nes(self):
		json_file = os.path.join(__location__,'serialized_biodoc.json')
		print(json_file)
		with open(json_file) as jf:
			biodoc = Document.load_from_JSON(json.load(jf))
		#test .nes for biodoc
		print(biodoc.nes)
		b1_gold_dict = {'TissueType': ['ventral nerve cord', 'neuron', 'nervous system'], 'CellType': ['neurons', 'neurons', 'neurons', 'neurons']}
		self.assertEqual(b1_gold_dict, biodoc.nes, "document-level nes dict for IOB entities was ill-formed")

		#test .nes for sentence
		s = biodoc.sentences[0]
		print(s.nes)
		s1_gold_dict = {'CellType': ['neurons'], 'TissueType': ['ventral nerve cord']}
		self.assertEqual(s1_gold_dict, s.nes, "sentence-level nes dict for IOB entities was ill-formed")

	#test non-bio text
	def test_obama_nes(self):
		json_file = os.path.join(__location__,'serialized_obama.json')
		print(json_file)
		with open(json_file) as jf:
			doc = Document.load_from_JSON(json.load(jf))
		#test .nes for doc
		print(doc.nes)
		d1_gold_dict = {'ORDINAL': ['44th', 'first', 'first'], 'LOCATION': ['US', 'United States', 'United States', 'Honolulu', 'Hawaii', 'Chicago', '13th District', 'United States'], 'NUMBER': ['1', '2', 'three'], 'DATE': ['August 4 , 1961', '1992 and 2004', '1997 to 2004', '2000'], 'ORGANIZATION': ['Columbia University', 'Harvard Law School', 'Harvard Law Review', 'University of Chicago Law School', 'Illinois Senate', 'House of Representatives'], 'MISC': ['American', 'African American', 'Democratic'], 'PERSON': ['Barack Hussein Obama II', 'Obama', 'Bobby Rush']}
		self.assertEqual(d1_gold_dict, doc.nes, "document-level nes dict for non-IOB entities was ill-formed")
		#test .nes for sentence
		s = doc.sentences[0]
		print(s.nes)
		s1_gold_dict = {'ORDINAL': ['44th'], 'DATE': ['August 4 , 1961'], 'NUMBER': ['1', '2'], 'LOCATION': ['US', 'United States'], 'ORGANIZATION': [], 'MISC': ['American'], 'PERSON': ['Barack Hussein Obama II']}
		self.assertEqual(s1_gold_dict, s.nes, "sentence-level nes dict for non-IOB entities was ill-formed")


if __name__ == "__main__":
    unittest.main()