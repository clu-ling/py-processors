#!/usr/bin/env python

# use data structures
from .ds import Document, Sentence, Dependencies
import json
import os
import shlex
import subprocess as sp
import requests


class Processor(object):
    PROC_VAR = 'PROCESSORS_SERVER'
    def __init__(self, address="http://127.0.0.1:8888/parse", jar_path=None):
        if jar_path:
            self.jar_path = os.path.expanduser(jar_path)
        else:
            try:
                self.jar_path = os.path.expanduser(os.environ[Processor.PROC_VAR])
            except:
                raise Exception("processors-server.jar not found.  Please add {} to your environment (ex. {}=/path/to/processors-server.jar)".format(Processor.PROC_VAR, Processor.PROC_VAR))
        self.address = address
        self._start_command = "java -cp {} NLPServer".format(self.jar_path)
        #self._start_server()

    def _start_server(self):
        self._process = sp.Popen(shlex.split(self._start_command), shell=False)

    def annotate(self, text):
        # POST json to the server API
        response = requests.post(self.address, json={"text":"{}".format(text)})
        # response content should be utf-8
        content = response.content.decode("utf-8")
        # load json and build Sentences and Document
        annotated_text = json.loads(content)
        parsed_sentences = annotated_text['sentences']
        sentences = []
        for i in parsed_sentences:
            s = parsed_sentences[i]
            words = s['words']
            lemmas = s['lemmas']
            tags = s['tags']
            entities = s['entities']
            deps = Dependencies(s['dependencies'], words)
            sentences.append(Sentence(words=words, lemmas=lemmas, tags=tags, entities=entities, dependencies=deps))
        return Document(text=text, sentences=sentences)

    def __del__(self):
        try:
            self._process.kill()
        except:
            print("Couldn't kill processors-server.  Was server started externally?")
