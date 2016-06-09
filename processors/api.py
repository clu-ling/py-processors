#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pkg_resources import resource_filename
from .processors import *
import os
import shlex
import os
import subprocess as sp
import requests
import time


class ProcessorsAPI(object):

    PROC_VAR = 'PROCESSORS_SERVER'

    def __init__(self, port, hostname="127.0.0.1", jar_path=None):

        self.hostname = hostname
        self.port = port
        self.make_address(hostname, port)
        self._start_command = "java -cp {} NLPServer {}"
        self.timeout = 120
        # processors
        self.default = Processor(self.address)
        self.fastnlp = FastNLPProcessor(self.address)
        self.bionlp = BioNLPProcessor(self.address)
        # use the os module's devnull for compatibility with python 2.7
        self.DEVNULL = open(os.devnull, 'wb')
        try:
            # Preference 1: if a .jar is given, check to see if the path is valid
            if jar_path:
                print("Using provided path")
                jp = os.path.expanduser(jar_path)
                # check if path is valid
                if os.path.exists(jp):
                    self.jar_path = jp
            else:
                # Preference 2: if a PROCESSORS_SERVER environment variable is defined, check its validity
                if ProcessorsAPI.PROC_VAR in os.environ:
                    print("Using path given via $PROCESSORS_SERVER")
                    jp = os.path.expanduser(os.environ[ProcessorsAPI.PROC_VAR])
                    # check if path is valid
                    if os.path.exists(jp):
                        self.jar_path = jp
                    else:
                        print("WARNING: {0} path is invalid.  \nPlease verify this entry in your environment:\n\texport {0}=/path/to/processors-server.jar".format(ProcessorsAPI.PROC_VAR))
                # Preference 3: attempt to use the processors-sever.jar downloaded when this package was installed
                else:
                    print("Using default")
                    self.jar_path = resource_filename(__name__, "processors-server.jar")
            # Attempt to start the server
            self._start_server()
        except Exception as e:
            print("processors-server.jar not found.  \nPlease start the server manually with .start_server(\"path/to/processors-server.jar\")")
            print("\n{}".format(e))

    def annotate(self, text):
        """
        Uses default processor (CoreNLP) to annotate text.  Included for backwards compatibility.
        """
        return self.default.annotate(text)

    def start_server(self, jar_path=None, timeout=120):
        self.timeout = int(float(timeout)/2)
        if jar_path:
            self.jar_path = jar_path
        self._start_server()

    def stop_server(self, port=None):
        port = port or self.port
        address = "http://{}:{}".format(self.hostname, port)
        shutdown_address = "{}/shutdown".format(address)
        response = requests.post(shutdown_address)
        if response:
            print(response.content.decode("utf-8"))
            return True
        return False

    def _start_server(self, port=None):
        if port:
            self.port = port
        # build the command
        cmd = self._start_command.format(self.jar_path, self.port)
        self._process = sp.Popen(shlex.split(cmd),
                                 shell=False,
                                 stderr=self.DEVNULL,
                                 stdout=self.DEVNULL,
                                 universal_newlines=True)

        print("Starting processors-server ({})...".format(self.jar_path))
        print("\nWaiting for server...")
        for i in range(self.timeout):
            try:
                success = self.annotate("blah")
                if success:
                    print("Connection with processors-server established!")
                    return True
            except Exception as e:
                #print(e)
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
