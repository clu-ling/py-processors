# A walkthrough example

The following examples give an overview of how to use `py-processors`.

## Getting started

For annotation and parsing, `py-processors` communicates with [`processors-server`](https://github.com/myedibleenso/processors-server) using a REST interface.

The server can be run either via `java` directly or in a [`docker` container](https://hub.docker.com/r/myedibleenso/processors-server/).  Let's look at how to connect to the server.

# Running the NLP server
### Option 1:  `processors-server.jar`
This method requires `java` and a compatible `processors-server.jar` for the server.  An appropriate `jar` will be downloaded automatically if one is not found.

```python
from processors import *
# The constructor requires you to specify a port for running the server.
API = ProcessorsAPI(port=8886)
```
_NOTE: It may take a minute or so for the server to initialize as there are some large model files that need to be loaded._

### Option 2:  `docker` container

You can pull [the official container from Docker Hub](https://hub.docker.com/r/myedibleenso/processors-server/):

```bash
docker pull myedibleenso/processors-server:latest
```

You can check `py-processors` for the appropriate version to retrieve:

```python
import processors
# print the recommended processors-server version
print(import processors.__ps_rec__)
```

Just replace `latest` in the command above with the appropriate version (`3.1.0` onwards).

The following command will run the container in the background and expose the service on port `8886`:

```bash
docker run -d -e _JAVA_OPTIONS="-Xmx3G" -p 127.0.0.1:8886:8888 --name procserv myedibleenso/processors-server
```
For a more detailed example showcasing configuration optionstake a look at [this `docker-compose.yml` file](https://github.com/myedibleenso/processors-server/blob/master/docker-compose.yml).  You'll need to map a local port to `8888` in the container.

Once the container is running, you can connect to it via `py-processors`:

```python
from processors import *
# provide the local port that you mapped to 8888 on the running container
API = ProcessorsBaseAPI(port=8886)
```

## Annotating text

Text can be annotated automatically with [these linguistic attributes](procesors.md#annotating-text).
```python
# try annotating some text using FastNLPProcessor (a CoreNLP wrapper)
doc = API.fastnlp.annotate("My name is Inigo Montoya.  You killed my father.  Prepare to die.")

# you can also annotate text already segmented into sentences
doc = API.fastnlp.annotate_from_sentences(["My name is Inigo Montoya.", "You killed my father.", "Prepare to die."])

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
s.bag_of_labeled_dependencies_using("tags")

# generate unlabeled dependencies using "words", "tags", "lemmas", "entities", or token index ("index")
s.bag_of_unlabeled_dependencies_using("lemmas")

# play around with the dependencies directly
deps = s.dependencies

# see what dependencies lead directly to the first token (i.e. token 0 is the dependent of what?)
deps.incoming[0]

# see what dependencies are originating from the first token (i.e. token 0 is the head of what?)
deps.outgoing[0]

# find all shortest paths between "name" and either "Inigo" or "Montoya".
deps.shortest_paths(start=1, end=[3,4])

# find the shortest path between "name" and either "Inigo" or "Montoya".  Prefer a path that involves a "nsubj" relation.
sp = deps.shortest_path(start=1, end=[3,4],
scoring_func=lambda path: 9000 if any(seg[1] == "nsubj" for seg in path) else 0)

# generate an Odin-like pattern with partial lexicalization
DependencyUtils.lexicalize_path(sentence=s, path=sp, lemmas=True, tags=True)

# limit lexicalization to tokens 1 and 4 (if present)
DependencyUtils.lexicalize_path(sentence=s, path=sp, lemmas=True, tags=True, limit_to=[1,4])

# run PageRank on the dependency graph to find nodes with the most activity.
# SPOILER: When using reverse=True, the nodes with the highest weight are usually the sentential predicate and its args
deps.pagerank(reverse=True)

# find out which nodes are most central to the dependency graph
deps.degree_centrality()

# retrieve the likely semantic head for a sentence.
from processors.paths import HeadFinder
doc2 = API.annotate("acute renal failure")
sentence = doc2.sentences[0]
# select the graph to examine (default is "stanford-collapsed") and
# optionally limit to a set of PoS tags (regex or str)
head_idx = sentence.semantic_head(graph_name="stanford-collapsed", valid_tags=None)
head_word = sentence.words[head_idx] if head_idx else None

# try using BioNLPProcessor
biodoc = api.bionlp.annotate("We next considered the effect of Ras monoubiquitination on GAP-mediated hydrolysis")

# check out the bio-specific entities
biodoc.nes
```

## Serializing to/from `json`

Once you've annotated text, you can serialize it to `json` for later loading.

```python
# serialize to/from JSON!
json_file = "serialized_doc_example.json"
ross_doc = api.fastnlp.annotate("We don't make mistakes, just happy little accidents.")

# serialize to JSON
with open(json_file, "w") as out:
    out.write(ross_doc.to_JSON())

# load from JSON
with open(json_file, "r") as jf:
    d = Document.load_from_JSON(json.load(jf))    
```

## Perform sentiment analysis

You can perform sentiment analysis using [`CoreNLP`'s tree-based system](https://nlp.stanford.edu/~socherr/EMNLP2013_RNTN.pdf).

```python
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

# ... or from text already segmented into sentences
lyrics = ["My sugar lumps are two of a kind", "Sweet and white and highly refined", "Honeys try all kinds of tomfoolery", "to steal a feel of my family jewelry"]
scores = API.sentiment.corenlp.score_segmented_text(lyrics)
```

## Rule-based information extraction (IE) with `Odin`  
If you're unfamiliar with writing `Odin` rules, see our manual for a primer on the language: [http://arxiv.org/pdf/1509.07513v1.pdf](http://arxiv.org/pdf/1509.07513v1.pdf)

```python
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
# visualize the structure of a mention as colored output in the terminal
for m in mentions: print(m)

# Alternatively, you can provide a rule URL.  The URL should end with .yml or .yaml.
rules_url = "https://raw.githubusercontent.com/clulab/reach/508697db2217ba14cd1fa0a99174816cc3383317/src/main/resources/edu/arizona/sista/demo/open/grammars/rules.yml"

mentions = API.odin.extract_from_text(example_text, rules_url)

# You can also perform IE with Odin on a Document.
barack_doc = API.annotate(example_text)
mentions = API.odin.extract_from_document(barack_doc, rules_url)

# mentions can be serialized as well
mentions_json_file = "mentions.json"

with open(mentions_json_file, "w") as out:
    out.write(JSONSerializer.mentions_to_JSON(mentions))

# loading from a file is also handled via JSONSerializer
with open(mentions_json_file, "r") as jf:
    mentions = JSONSerializer.mentions_from_JSON(json.load(jf))
```

# `Jupyter` notebook visualizations

`py-processors` supports some custom notebook-based visualizations, but  you'll need to install the extra `[jupyter]` module in order to use them:

```
pip install "py-processors[jupyter]"
```

These visualizations make use of [our fork](https://github.com/myedibleenso/displacy-processors) of [displaCy](https://github.com/explosion/displacy), You can now visualize a `Sentence` graph as an SVG image using `visualization.JupyterVisualizer.display_graph()`:

```python
from processors.visualization import JupyterVisualizer as viz
# run this snippet within a jupyter notebook
text = "To be loved by unicorns is the greatest gift of all."
doc = API.annotate(text)
viz.display_graph(doc.sentences[0], graph_name="stanford-collapsed")
```

Mentions can also be visualized in a notebook:

```python
# run this snippet within a jupyter notebook
rules = """
rules:
  - name: "ner-location"
    label: [Location, PossibleLocation, Entity]
    priority: 1
    type: token
    pattern: |
      [entity="LOCATION"]+ | Twin Peaks

  - name: "ner-person"
    label: [Person, PossiblePerson, Entity]
    priority: 1
    type: token
    pattern: |
     [entity="PERSON"]+

  - name: "ner-org"
    label: [Organization, Entity]
    priority: 1
    type: token
    pattern: |
      [entity="ORGANIZATION"]+

  - name: "ner-date"
    label: [Date]
    priority: 1
    type: token
    pattern: |
      [entity="DATE"]+

  - name: "missing"
    label: Missing
    pattern: |
      trigger = [lemma=go] missing
      theme: Person = <xcomp nsubj
      date: Date? = prep_on
"""
mentions = API.odin.extract_from_text("FBI Special Agent Dale Cooper went missing on June 10, 1991.  He was last seen in the woods of Twin Peaks. ", rules=rules)

for m in mentions: viz.display_mention(m)
```


# Other ways of initializing the server

## Using a custom `processors-server`

When initializing the API, you can specify a path to a custom `processors-server.jar` using the `jar_path` parameter:

```python
from processors import *

API = ProcessorsAPI(port=8886, jar_path="path/to/processors-server.jar")
```

Alternatively, you can set an environment variable, `PROCESSORS_SERVER`, with the path to the `jar` you wish to use.  In your `.bashrc` (or equivalent), add this line with the path to the `jar` you wish to use with `py-processors`:

```bash
export PROCESSORS_SERVER="path/to/processors-server.jar"
```

Remember to `source` your `profile`:
```bash
source path/to/your/.profile
```

`py-processors` will now prefer this jar whenever a new API is initialized.

_NOTE: If you decide that you no longer want to use this enivronment variable, remember to both remove it from your profile and run_ `unset PROCESSORS_SERVER` _from the shell._

## Allocating memory

By default, the server will be run with 3GB of RAM. You might be able to get by with a little less, though.  You can start the server with a different amount of memory with the `jvm_mem` parameter:

```python
from processors import *
# run the sever with 2GB of memory
API = ProcessorsAPI(port=8886, jvm_mem="-Xmx2G")
```

_NOTE: This won't have any effect if the server is already running on the given port._

# Keeping the server running

If you've launched the server via `java`, `py-processors` will by default attempt to shut down the server whenever an API instance goes out of scope (ex. your script finishes or you exit the interpreter).  

If you'd prefer to keep the server alive, you'll need to initialize the API with `keep_alive=True`:

```python
from processors import *

API = ProcessorsAPI(port=8886, keep_alive=True)
```

This is useful if you're sharing access to the server on a network, or if you have a bunch of independent tasks and would prefer to avoid waiting for the server to initialize again and again.
