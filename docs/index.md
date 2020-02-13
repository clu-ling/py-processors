[![Documentation Status](https://readthedocs.org/projects/py-processors/badge/?version=latest)](http://py-processors.readthedocs.io/en/latest/?badge=latest) [![Pypi version](https://img.shields.io/pypi/v/py-processors.svg)](https://pypi.python.org/pypi/py-processors)  [![Build Status](https://travis-ci.org/clu-ling/py-processors.svg?branch=master)](https://travis-ci.org/clu-ling/py-processors) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/clu-ling/py-processors/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/clu-ling/py-processors/?branch=master) [![Coverage Status](https://coveralls.io/repos/github/clu-ling/py-processors/badge.svg?branch=master)](https://coveralls.io/github/clu-ling/py-processors?branch=master) [![Requirements Status](https://requires.io/github/clu-ling/py-processors/requirements.svg?branch=master)](https://requires.io/github/clu-ling/py-processors/requirements/?branch=master)

# Contents
- [Text processors](processors.md)
- [Rule-based IE with Odin](odin.md)
- [Annotating text](processors.md#annotating-text)
- [API Reference](api.md)
- [A walkthrough example](example.md)
- [Running the tests](dev.md#running-the-tests)
- [FAQ](faq.md)
- [History](release-notes.md)

# What is it?
`py-processors` is a Python wrapper for the CLU Lab's [`processors`](http://github.com/clulab/processors) NLP library.  `py-processors` relies on [`processors-server`](http://github.com/clu-ling/processors-server).  

# Requirements
The server component can be run either via `docker` or directly with `java`.

## Option 1
- [`docker`](https://www.docker.com/) and the [`clu-ling/processors-server`](https://hub.docker.com/r/parsertongue/processors-server/) container

## Option 2
- [≥ Java 8](https://openjdk.java.net/install/)
- [`processor-server`](http://github.com/clu-ling/processors-server) (v3.1.0)
  - this dependency will be retrieved automatically during installation
- At least 2GB of RAM free for the server (I recommend 3GB+)

# Installation

`py-processors` can be installed via `pip`.  The library also has a `jupyter` extras module which adds widgets/visualizations to `juypter` notebooks.

### basic installation
```bash
pip install py-processors
```

### basic + `jupyter` notebook widgets
```bash
pip install py-processors[jupyter]
```

### bleeding edge
```bash
pip install git+https://github.com/clu-ling/py-processors.git
```

# How to use it?

See [the walkthrough example](example.md)
