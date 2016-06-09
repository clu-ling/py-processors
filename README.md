[![Stories in Ready](https://badge.waffle.io/myedibleenso/py-processors.svg?label=ready&title=Ready)](http://waffle.io/myedibleenso/py-processors)[![Build Status](https://travis-ci.org/myedibleenso/py-processors.svg?branch=master)](https://travis-ci.org/myedibleenso/py-processors)[![Coverage Status](https://coveralls.io/repos/github/myedibleenso/py-processors/badge.svg?branch=master)](https://coveralls.io/github/myedibleenso/py-processors?branch=master)

# What is it?
`py-processors` is a Python wrapper for the CLU Lab's [`processors`](http://github.com/clulab/processors) NLP library.  `py-processors` relies on [`processors-server`](http://github.com/myedibleenso/processors-server).  

Though ([mostly](https://github.com/myedibleenso/py-processors/issues?q=is%3Aopen+is%3Aissue+label%3Apython2.x)) compatible with Python 2.x, this library was developed with 3.x in mind.

# Requirements
- Java 8

# Installation

```bash
pip install git+https://github.com/myedibleenso/py-processors.git
```

# How to use it?

```python
from processors import *

# The constructor requires you to specify a port for running the server.
# You can also provide a jar path to the constructor, if you haven't already
# set a PROCESSORS_SERVER environment variable.
api = ProcessorsAPI(port=8886)

# Start the server (optionally provide the path to the jar).
# It may take a minute or so to load the large model files.
api.start_server("path/to/processors-server.jar")

# try annotating some text using FastNLPProcessor (a CoreNLP wrapper)
doc = api.fastnlp.annotate("My name is Inigo Montoya.  You killed my father.  Prepare to die.")

# There should be 3 Sentence objects in this Document
len(doc.sentences)

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
```

# Running the tests

1. Clone and install the package locally:
```bash
git clone https://github.com/myedibleenso/py-processors.git
cd py-processors
pip install -e .
```
2. Run the tests
```bash
green -vv --run-coverage
```

# I want the latest `processors-server.jar`
In that case, take a look over [here](https:github.com/myedibleenso/processors-server).

# Issues
### Something is already running on port `XXXX`, but I don't know what.  Help!

Try running the following command:

```bash
lsof -i :<portnumber>
```
You can then kill the responsible process using the reported `PID`
