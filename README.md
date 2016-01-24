# What is it?
Python wrapper for the CLU Lab's [`processors`](http://github.com/clulab/processors) NLP library.  Relies on the [`processors-server`](http://github.com/myedibleenso/processors-server).

# Requirements
- Java 8

# Installation

```
git clone https://github.com/myedibleenso/py-processors.git
pip install -e py-processors
```

### Grab the `processors-server` fat `jar`

```
wget http://www.cs.arizona.edu/~hahnpowell/processors-server/current/processors-server.jar
```

or
```
curl -H "Accept: application/zip" http://www.cs.arizona.edu/~hahnpowell/processors-server/current/processors-server.jar -o processors-server.jar
```

# How to use it?

```python
from processors import *

# the constructor requires you to specify a port to run the server on
proc = Processor(port=8886)

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
```

# Issues
### Something is already running on port `XXXX`, but I don't know what.  Help!

Try running the following command:

```
lsof -i :<portnumber>
```
You can then kill the responsible process using the reported `PID`
