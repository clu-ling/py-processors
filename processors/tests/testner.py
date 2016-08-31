from __future__ import print_function
from processors import *


api = ProcessorsAPI(port=8886)

def try_bio_ner():
	filename = 'serialized_biodoc.json'
	with open(filename) as jf:
	    data = Document.load_from_JSON(json.load(jf))
	    print(data.nes)
	    sentence = data.sentences[5]
	    print(sentence.nes)

try_bio_ner()
#print(data.nes)
#{'Family': ['this family', '3a'], 'Site': ['link', 'link', 'link', 'link', 'orange', 'orange', 'link', 'link'], 'Species': ['arabidopsis thaliana', 'a. thaliana', 'arabidopsis thaliana', 'a. thaliana', 'dogs', 'arabidopsis thaliana', 'a. thaliana', 'a. thaliana', 'name', 'name', 'name', 'a. thaliana', 'a. thaliana', 'a. thaliana', 'arabidopsis thaliana', 'a. thaliana', 'a. thaliana', 'name', 'name', 'thale cress', 'a. thaliana', 'name', 'name', 'name', 'mouse', 'a. thaliana', 'a. thaliana', 'name', 'a. thaliana', 'name', 'a. thaliana', 'arabidopsis thaliana', 'a. thaliana', 'a. thaliana'], 'BioProcess': ['circadian rhythm', 'circadian rhythm', 'circadian rhythm', 'circadian rhythm', 'transcription', 'circadian rhythm'], 'Cellular_component': ['nucleus', 'chromosomes', 'chromosomes', 'chromosome', 'chromosomes', 'chromosomes', 'chromosomes', 'chromosomes'], 'Simple_chemical': ['sulforaphane', 'alpha', 'alpha', 'alpha', '5b'], 'Gene_or_gene_product': ['rapa', 'toc1 gene', 'rapa', 'toc1 genes', 'step', 'rapa', 'toc1 gene', 'rapa', 'toc1 genes', 'step', 'rapa', 'b. napus nagaharu', 'crop', '~ 120 \\ u2009mb', 'rapa', 'parkin', 'parkin', 'rapa', 'parkin', 'parkin', 'rapa', 'gamma eudicot paleohexaploidy.', 'parkin', 'rapa', 'rapa', 'brassica', 'rapa', 'toc1', 'task', 'wiki available1', 'http://genomevolution.org/r/4a3', 'rapa', 'rapa', '~ 1', 'rapa', 'http://genomevolution.org/r/4sr4', 'rapa', 'synmap', 'synmap', 'synmap', 'rapa', 'rapa', 'http://genomevolution.org/r/4skv', 'http://genomevolution.org/r/4sl1', 'rapa', 'http://genomevolution.org/r/4sl5', 'koonin', 'rapa', 'id1', 'v10', 'id11022', 'rapa', 'rapa', 'http://genomevolution.org/r/4ss2', 'http://genomevolution.org/r/4ss3', 'ks histogram', 'http://genomevolution.org/r/4sl1', 'http://genomevolution.org/r/4sl5', 'step', 'synmap', 'synmap', 'cds protein coding sequence', 'blast3', 'rapa', 'toc1', 'ppr protein family pseudo response regulators', 'ppr family', 'toc1', 'tobin', 'toc1', 'rapa', 'toc1', 'rapa', 'toc1', 'br1', 'rapa', 'toc1 gene', 'http://genomevolution.org/r/4smb', 'http://genomevolution.org/r/4smc', 'toc1', 'rapa', 'rapa', 'toc1 syntenic regions', 'http://genomevolution.org/r/4sz5 pedersen', 'http://genomevolution.org/r/4sz6', 'hsps', 'http://genomevolution.org/r/4smb', 'toc1', 'rapa', 'step', 'toc1', 'arabidopsis toc1 gene', 'rapa', 'cnss', 'bra035933', 'bra029310', 'toc1', 'blastn', 'bra035933', 'rapa', 'rapa', 'rapa', 'toc1', 'rapa', 'rapa', 'toc1', 'neo'], 'CellLine': ['beta', 'focus', 'focus', 'time', 'case', 'cost', 'time', 'time', 'case', '4a', '4b', '4d', '4c', '4b', '4d', '4e', 'button', '4b', 'time', 'time', 'time', 'line', 'button', '5a', '5a', 'line', 'line', '5c', '5a', 'case', 'button', 'time', 'blue', 'line', 'case'], 'Organ': ['organism', 'organism', 'organism', 'organism', 'organism', 'organism', 'organism', 'organism', 'organism', 'organism', 'tips', 'organism', 'scales'], 'TissueType': ['style', 'style', 'fiber', 'leaf', 'tail']}
#print(sentence.nes)
#defaultdict(<class 'list'>, {'Gene_or_gene_product': ['toc1 gene', 'rapa'], 'BioProcess': ['circadian rhythm'], 'Site': [], 'CellLine': [], 'Simple_chemical': [], 'TissueType': [], 'Organ': [], 'Family': [], 'Species': ['a. thaliana'], 'Cellular_component': []})


def try_obama_ner():
	filename = 'obama.txt'
	text = open(filename, 'r')
	text = text.read()
	doc = api.fastnlp.annotate(text)
	print(doc.nes)
	s = doc.sentences[0]
	print(s.nes)

try_obama_ner()
#print doc nes
#{'LOCATION': ['US', 'United States', 'United States', 'Honolulu', 'Hawaii', 'Chicago', '13th District', 'United States'], 'ORGANIZATION': ['Columbia University', 'Harvard Law School', 'Harvard Law Review', 'University of Chicago Law School', 'Illinois Senate', 'House of Representatives'], 'ORDINAL': ['44th', 'first', 'first'], 'MISC': ['American', 'African American', 'Democratic'], 'PERSON': ['Barack Hussein Obama II', 'Obama', 'Bobby Rush'], 'NUMBER': ['1', '2', 'three'], 'DATE': ['August 4 , 1961', '1992 and 2004', '1997 to 2004', '2000']}
#print sentence nes
#defaultdict(<class 'list'>, {'PERSON': ['Barack Hussein Obama II'], 'MISC': ['American'], 'DATE': ['August 4 , 1961'], 'ORDINAL': ['44th'], 'LOCATION': ['US', 'United States'], 'NUMBER': ['1', '2'], 'ORGANIZATION': []})

