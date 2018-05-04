#!/usr/bin/env python
# -*- coding: utf-8 -*-

# use data structures
from __future__ import unicode_literals
from processors.ds import Document, Sentence, DirectedGraph
from processors.utils import post_json
import json


class Processor(object):
    """
    Base Processor for text annotation (tokenization, sentence splitting,
    parsing, lemmatization, PoS tagging, named entity recognition, chunking, etc.).

    Parameters
    ----------
    address : str
        The base address for the API (i.e., everything preceding `/api/..`)


    Attributes
    ----------
    service : str
        The API endpoint for `annotate` requests.

    Methods
    -------
    annotate(text)
        Produces an annotated `Document` from the provided text.
    annotate_from_sentences(sentences)
        Produces an annotated `Document` from a [str] of text already split into sentences.

    """
    def __init__(self, address):
        self.service = "{}/api/annotate".format(address)

    def _message_to_json_dict(self, msg):
        return post_json(self.service, msg.to_JSON())

    def _annotate_message(self, msg):
        annotated_text = post_json(self.service, msg.to_JSON())
        return Document.load_from_JSON(annotated_text)

    def annotate(self, text):
        """
        Annotate text (tokenization, sentence splitting,
        parsing, lemmatization, PoS tagging, named entity recognition, chunking, etc.)

        Parameters
        ----------
        text : str
            `text` to be annotated.

        Returns
        -------
        processors.ds.Document or None
            An annotated Document composed of `sentences`.
        """
        try:
            # load json and build Sentences and Document
            msg = Message(text)
            return self._annotate_message(msg)

        except Exception as e:
            #print(e)
            return None

    def annotate_from_sentences(self, sentences):
        """
        Annotate text that has already been segmented into `sentences`.

        Parameters
        ----------
        sentences : [str]
            A list of str representing text already split into sentences.

        Returns
        -------
        processors.ds.Document or None
            An annotated `Document` composed of `sentences`.
        """
        try:
            # load json from str interable and build Sentences and Document
            msg = SegmentedMessage(sentences)
            return self._annotate_message(msg)

        except Exception as e:
            #print(e)
            return None

class CluProcessor(Processor):

    """
    Processor for text annotation based on [`org.clulab.processors.clu.CluProcessor`](https://github.com/clulab/processors/blob/master/main/src/main/scala/org/clulab/processors/clu/CluProcessor.scala)

    Uses the Malt parser.
    """
    def __init__(self, address):
        self.service = "{}/api/clu/annotate".format(address)

    def annotate(self, text):
        return super(CluProcessor, self).annotate(text)

class BioCluProcessor(Processor):

    """
    Processor for text annotation based on [`org.clulab.processors.clu.BioCluProcessor`](https://github.com/clulab/processors/blob/master/main/src/main/scala/org/clulab/processors/clu/CluProcessor.scala)

    Uses the Malt parser.
    """
    def __init__(self, address):
        self.service = "{}/api/clu/bio/annotate".format(address)

    def annotate(self, text):
        return super(BioCluProcessor, self).annotate(text)


class CluService(object):
    """
    Manages processors under clu package

    Parameters
    ----------
    address : str
        The base address for the API (i.e., everything preceding `/api/..`)

    Methods
    -------
    annotate(text)
        Produces a Document from the provided `text` using the default processor (CluProcessor).
    clu.annotate(text)
        Produces a Document from the provided `text` using the default processor (CluProcessor).
    bio.annotate(text)
        Produces a Document from the provided `text` using BioCluProcessor.
    """
    def __init__(self, address):
        self.clu = CluProcessor(address)
        self.bio = BioCluProcessor(address)

    def annotate(self, text):
        return self.clu.annotate(text)

class FastNLPProcessor(Processor):

    """
    Processor for text annotation based on [`org.clulab.processors.fastnlp.FastNLPProcessor`](https://github.com/clulab/processors/blob/master/corenlp/src/main/scala/org/clulab/processors/fastnlp/FastNLPProcessor.scala)

    Uses the Stanford CoreNLP neural network parser.
    """
    def __init__(self, address):
        self.address = address
        self.service = "{}/api/fastnlp/annotate".format(address)
        self.chunk_address = "{}/api/fastnlp/chunk".format(self.address)


    def annotate(self, text):
        return super(FastNLPProcessor, self).annotate(text)

    def _chunk(self, obj):
        return post_json(self.chunk_address, obj.to_JSON())

    def chunk_sentence(self, sentence):
        res = self._chunk(sentence)
        return Sentence.load_from_JSON(res)

    def chunk_document(self, doc):
        res = self._chunk(doc)
        return Document.load_from_JSON(res)


class BioNLPProcessor(Processor):

    """
    Processor for biomedical text annotation based on [`org.clulab.processors.fastnlp.FastNLPProcessor`](https://github.com/clulab/processors/blob/master/corenlp/src/main/scala/org/clulab/processors/fastnlp/FastNLPProcessor.scala)

    CoreNLP-derived annotator.

    """

    def __init__(self, address):
        self.service = "{}/api/bionlp/annotate".format(address)

    def annotate(self, text):
        return super(BioNLPProcessor, self).annotate(text)


class Message(object):

    """
    A storage class for passing `text` to API `annotate` endpoint.

    Attributes
    ----------
    text : str
        The `text` to be annotated.

    Methods
    -------
    to_JSON()
        Produces a json str in the structure expected by the API `annotate` endpoint.

    """
    def __init__(self, text):
        self.text = text

    def to_JSON_dict(self):
        jdict = dict()
        jdict["text"] = self.text
        return jdict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)


class SegmentedMessage(object):
    """
    A storage class for passing text already split into sentences to API `annotate` endpoint.

    Attributes
    ----------
    segments : [str]
        Text to be annotated that has already been split into sentences.  This segmentation is preserved during annotation.

    Methods
    -------
    to_JSON()
        Produces a json str in the structure expected by the API `annotate` endpoint.

    """
    def __init__(self, segments):
        self.segments = segments

    def to_JSON_dict(self):
        jdict = dict()
        jdict["segments"] = self.segments
        return jdict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)
