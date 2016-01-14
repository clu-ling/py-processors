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

# Issues
### Something is already running on port `8888`, but I don't know what.  Help!

I will eventually change `processors-server` to optionally take a port as a command line argument.  You'll be able to specify this in `.start_server()`.  For the time being, though...

Try running the following command:

```
lsof -i :8888
```
You can then kill the responsible process using the reported PID
