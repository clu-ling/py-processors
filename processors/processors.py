#!/usr/bin/env python

# use data structures
from .ds import Document, Sentence, Dependencies
import json
import os
import shlex
import os
import subprocess as sp
import requests
import time


class Processor(object):
    PROC_VAR = 'PROCESSORS_SERVER'
    def __init__(self, hostname="127.0.0.1", port=8888, jar_path=None):

        self.hostname = hostname
        self.port = port
        self.address = self._make_address()
        self._start_command = "java -cp {} NLPServer"
        self.timeout = 120
        if jar_path:
            self.jar_path = os.path.expanduser(jar_path)
            # attempt to start the server
            self._start_server()
        else:
            try:
                # use the os module's devnull for compatibility with python 2.7
                self.DEVNULL = open(os.devnull, 'wb')
                self.jar_path = os.path.expanduser(os.environ[Processor.PROC_VAR])
                if not os.path.exists(self.jar_path):
                    raise Exception
                self._start_server()
            except Exception as e:
                print("WARNING: processors-server.jar not found.  \nPlease start the server using start_server(/path/to/processors-server.jar).  \nAvoid this error in the future by adding {} to your environment:\n\t{}=/path/to/processors-server.jar".format(Processor.PROC_VAR, Processor.PROC_VAR))

    def start_server(self, jarpath=None, timeout=120):
        self.timeout = int(float(timeout)/2)
        if jarpath:
            self.jar_path = jarpath
        self._start_server()

    def _start_server(self):
        self._process = sp.Popen(shlex.split(self._start_command.format(self.jar_path)),
                                             shell=False,
                                             stderr=self.DEVNULL,
                                             stdout=self.DEVNULL,
                                             universal_newlines=True)

        print("Starting processors-server...")
        for i in range(self.timeout):
            try:
                success = self.annotate("blah")
                if success:
                    print("Connection with processors-server established!")
                    return True
            except:
                # wait and try again
                time.sleep(2)
        # if the server still hasn't started, raise an Exception
        raise Exception("Couldn't connect to processors-server. Is the port in use?")

    def _make_address(self):
        return "http://{}:{}/parse".format(self.hostname, self.port)

    def make_address(self, hostname, port):
        # update hostname
        self.hostname = hostname
        # update port
        self.port = port
        # update address
        self.address = self._make_address()

    def _get_path(self, p):
        """
        Expand a user-specified path.  Supports "~" shortcut.
        """
        return os.path.abspath(os.path.normpath(os.path.expanduser(p)))

    def annotate(self, text):
        try:
            # POST json to the server API
            #response = requests.post(self.address, json={"text":"{}".format(text)})
            # for older versions of requests, use the call below
            response = requests.post(self.address,
                                    data=json.dumps({"text":"{}".format(text)}),
                                    headers={"content-type": "application/json"})
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
        except:
            raise Exception("Connection refused!  Is the server running?")

    def __del__(self):
        """
        Stop server
        """
        try:
            self._process.kill()
            # close our file object
            self.DEVNULL.close()
            print("Successfully shut down processors-server!")
        except:
            print("Couldn't kill processors-server.  Was server started externally?")
