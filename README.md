# What is it?
Python wrapper for the CLU Lab's [`processors`]() NLP library.  Relies on the [`processors-server`]().

# Installation

```
git clone https://github.com/myedibleenso/py-processors.git
pip install -e py-processors
```
# How to use it?

### Running `processors-server`
Eventually the `processors-server.jar` will be bundled with this library.  For now you can get it here (requires `Java 8` and `Scala 2.11.x`):
```
git clone https://github.com/myedibleenso/processors-server.git
```
Fire up the server.
```
cd processors-server
sbt "runMain NLPServer"
```
It may take a minute or so to load the large model files.

### Using `py-processors`

```
from processors import *
proc = Processor()
doc = proc.annotate("My name is Inigo Montoya.  You killed my father.  Prepare to die.")

# There should be 3 Sentence objects in this Document
len(doc.sentences)

# A Document contains the words, pos tags, lemmas, named entities, and syntactic dependencies of its component Sentences
doc.bag_of_labeled_deps

# We can access the Named Entities for the Document as a dictionary mapping an NE Label -> List[String]
doc.nes

# A Sentence contains words, pos tags, lemmas, named entities, and syntactic dependencies
doc.sentences[0].lemmas
