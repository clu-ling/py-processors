# What is it?
Python wrapper for the CLU Lab's [`processors`]() NLP library.  Relies on the [`processors-server`]().

# Requirements
- Java 8

# Installation

```
git clone https://github.com/myedibleenso/py-processors.git
pip install -e py-processors
```
### Grab the `processors-server` fat `jar`

`wget http://www.cs.arizona.edu/~hahnpowell/processors-server/current/processors-server.jar`

or

`curl -H "Accept: application/zip" http://www.cs.arizona.edu/~hahnpowell/processors-server/current/processors-server.jar -o processors-server.jar`

# How to use it?

```python
from processors import *
proc = Processor()

# Start the server.
# It may take a minute or so to load the large model files.
proc.start_server(path/to/processors-server.jar)

doc = proc.annotate("My name is Inigo Montoya.  You killed my father.  Prepare to die.")

# There should be 3 Sentence objects in this Document
len(doc.sentences)

# A Document contains the words, pos tags, lemmas, named entities, and syntactic dependencies of its component Sentences
doc.bag_of_labeled_deps

# We can access the named entities for the Document as a dictionary mapping an NE label -> list of named entities
doc.nes

# A Sentence contains words, pos tags, lemmas, named entities, and syntactic dependencies
doc.sentences[0].lemmas
```
