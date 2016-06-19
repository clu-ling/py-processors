# A walkthrough example

The following bit of code gives an overview of `py-processors`.

```python
from processors import *

# The constructor requires you to specify a port for running the server.
# You can also provide a jar path to the constructor, if you haven't already
# set a PROCESSORS_SERVER environment variable.
# By default, the server will be run with 3G of RAM.  
# If you only have 2G available, use jvm_mem="-Xmx2G"
API = ProcessorsAPI(port=8886)
# If ProcessorsAPI is unable to find a valid path to a processors-server.jar,
# you'll need to start the server manually (optionally provide the path to the jar).
# It may take a minute or so to load the large model files.
# API.start_server("path/to/processors-server.jar")

# try annotating some text using FastNLPProcessor (a CoreNLP wrapper)
doc = API.fastnlp.annotate("My name is Inigo Montoya.  You killed my father.  Prepare to die.")

# There should be 3 Sentence objects in this Document
doc.size

# A Document contains the words, pos tags, lemmas, named entities, and syntactic dependencies of its component Sentences
doc.bag_of_labeled_deps

# We can access the named entities for the Document as a dictionary mapping an NE label -> list of named entities
doc.nes

# A Sentence contains words, pos tags, lemmas, named entities, and syntactic dependencies
doc.sentences[0].lemmas

# get the first sentence
s = doc.sentences[0]

# the number of tokens in this sentence
s.length

# the named entities contained in this sentence
s.nes

# generate labeled dependencies using "words", "tags", "lemmas", "entities", or token index ("index")
s.labeled_dependencies_using("tags")

# generate unlabeled dependencies using "words", "tags", "lemmas", "entities", or token index ("index")
s.unlabeled_dependencies_using("lemmas")

# play around with the dependencies directly
deps = s.dependencies

# see what dependencies lead directly to the first token (i.e. token 0 is the dependent of what?)
deps.incoming[0]

# see what dependencies are originating from the first token (i.e. token 0 is the head of what?)
deps.outgoing[0]

# try using BioNLPProcessor
biodoc = api.bionlp.annotate("We next considered the effect of Ras monoubiquitination on GAP-mediated hydrolysis")

# check out the bio-specific entities
biodoc.nes

# serialize to/from JSON!
json_file = "serialized_doc_example.json"
ross_doc = api.fastnlp.annotate("We don't make mistakes, just happy little accidents.")

# serialize to JSON
with open(json_file, "w") as out:
    out.write(ross_doc.to_JSON())

# load from JSON
with open(json_file, "r") as jf:
    d = Document.load_from_JSON(json.load(jf))    

# get sentiment analysis scores
review = "The humans are dead."
doc = API.fastnlp.annotate(review)

# try Stanford's tree-based sentiment analysis
# you'll get a score for each Sentence
# scores are between 1 (very negative) - 5 (very positive)
scores = API.sentiment.corenlp.score_document(doc)

# you can pass text directly
scores = API.sentiment.corenlp.score_text(review)

# ... or a single sentence
score = API.sentiment.corenlp.score_sentence(doc.sentences[0])

# Do rule-based IE with Odin!
# see http://arxiv.org/pdf/1509.07513v1.pdf for details
example_rule = """
- name: "ner-person"
  label: [Person, PossiblePerson, Entity]
  priority: 1
  type: token
  pattern: |
   [entity="PERSON"]+
   |
   [tag=/^N/]* [tag=/^N/ & outgoing="cop"] [tag=/^N/]*
"""

example_text = """
Barack Hussein Obama II is the 44th and current President of the United States and the first African-American to hold the office.
He is a Democrat.
Obama won the 2008 United States presidential election, on November 4, 2008.
He was inaugurated on January 20, 2009.
"""

# take a look at the .label, .labels, and .text attributes of each mention
mentions = API.odin.extract_from_text(example_text, example_rule)

# Alternatively, you can provide a rule URL.  The URL should end with .yml or .yaml.
rules_url = "https://raw.githubusercontent.com/clulab/reach/508697db2217ba14cd1fa0a99174816cc3383317/src/main/resources/edu/arizona/sista/demo/open/grammars/rules.yml"

mentions = API.odin.extract_from_text(example_text, rules_url)

# You can also perform IE with Odin on a Document.
barack_doc = API.annotate(example_text)
mentions = API.odin.extract_from_document(barack_doc, rules_url)
```
