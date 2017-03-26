[![Documentation Status](https://readthedocs.org/projects/py-processors/badge/?version=latest)](http://py-processors.readthedocs.io/en/latest/?badge=latest) [![Pypi version](https://img.shields.io/pypi/v/py-processors.svg)](https://pypi.python.org/pypi/py-processors)  [![Build Status](https://travis-ci.org/myedibleenso/py-processors.svg?branch=master)](https://travis-ci.org/myedibleenso/py-processors) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/myedibleenso/py-processors/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/myedibleenso/py-processors/?branch=master) [![Coverage Status](https://coveralls.io/repos/github/myedibleenso/py-processors/badge.svg?branch=master)](https://coveralls.io/github/myedibleenso/py-processors?branch=master) [![Requirements Status](https://requires.io/github/myedibleenso/py-processors/requirements.svg?branch=master)](https://requires.io/github/myedibleenso/py-processors/requirements/?branch=master)

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
`py-processors` is a Python wrapper for the CLU Lab's [`processors`](http://github.com/clulab/processors) NLP library.  `py-processors` relies on [`processors-server`](http://github.com/myedibleenso/processors-server).  

Though [compatible*](https://github.com/myedibleenso/py-processors/issues?q=is%3Aopen+is%3Aissue+label%3Apython2.x) with Python 2.x, this library was developed with 3.x in mind.

# Requirements
- [Java 8](https://docs.oracle.com/javase/8/docs/technotes/guides/install/install_overview.html)
- [`processor-sever`](http://github.com/myedibleenso/processors-server) (v3.0)
  - this dependency will be retrieved automatically during installation
- At least 2GB of RAM free for the server (I recommend 3GB)

# Installation

```bash
pip install git+https://github.com/myedibleenso/py-processors.git
```

# How to use it?

See [the walkthrough example](example.md)
