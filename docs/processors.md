# Overview

This page provides an overview of the available text processing pipelines.

# Annotating text

a `.annotate` call produces a `Document` with the following features:
- sentence segmentation
- tokenization
- part-of-speech tagging
- lemmatization
- named entity recognition
- syntactic dependency parsing


Annotation suitable to open domain text can be performed with either a `.annotate` or a `.fastnlp.annotate` call:

```python
API = ProcessorsAPI(port=8886)
# annotate the provided text using FastNLPProcessor (a CoreNLP wrapper)
doc = API.fastnlp.annotate("My name is Inigo Montoya.  You killed my father.  Prepare to die.")
```

For annotation tuned to the biomedical domain, use `.bionlp.annotate`:

```python
API = ProcessorsAPI(port=8886)
doc = API.bionlp.annotate("In contrast, the EGFR T669A mutant increased both basal EGFR and ERBB3 tyrosine phosphorylation that was not augmented by MEK inhibition.")
```

# API Reference

See [the API reference](api.md) for more details.
