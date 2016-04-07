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
    def __init__(self, port, hostname="127.0.0.1", jar_path=None):

        self.hostname = hostname
        self.port = port
        self.make_address(hostname, port)
        self._start_command = "java -cp {} NLPServer {}"
        self.timeout = 120
        # use the os module's devnull for compatibility with python 2.7
        self.DEVNULL = open(os.devnull, 'wb')
        if jar_path:
            self.jar_path = os.path.expanduser(jar_path)
            # attempt to start the server
            self._start_server()
        else:
            try:
                self.jar_path = os.path.expanduser(os.environ[Processor.PROC_VAR])
                if not os.path.exists(self.jar_path):
                    raise Exception
                self._start_server()
            except Exception as e:
                print("WARNING: processors-server.jar not found.  \nPlease start the server using start_server(/path/to/processors-server.jar).  \nAvoid this error in the future by adding {} to your environment:\n\t{}=/path/to/processors-server.jar".format(Processor.PROC_VAR, Processor.PROC_VAR))

    def start_server(self, port, jarpath=None, timeout=120):
        self.port = port
        self.timeout = int(float(timeout)/2)
        if jarpath:
            self.jar_path = jarpath
        self._start_server()

    def stop_server(self, port=None):
        port = port or self.port
        address = "http://{}:{}".format(self.hostname, port)
        shutdown_address = "{}/shutdown".format(address)
        response = requests.post(shutdown_address)
        if response:
            print(response.content.decode("utf-8"))

    def _start_server(self, port=None):
        if port:
            self.port = port
        self._process = sp.Popen(shlex.split(self._start_command.format(self.jar_path, self.port)),
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

    def make_address(self, hostname, port):
        # update hostname
        self.hostname = hostname
        # update port
        self.port = port
        # update address
        self.address = "http://{}:{}".format(self.hostname, self.port)

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
            annotate_service_address = "{}/annotate".format(self.address)
            response = requests.post(annotate_service_address,
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
            self.stop_server()
            # close our file object
            self.DEVNULL.close()
            print("Successfully shut down processors-server!")
        except:
            print("Couldn't kill processors-server.  Was server started externally?")
