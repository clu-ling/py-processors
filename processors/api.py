#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#from pkg_resources import resource_filename
try:
    from urllib import urlretrieve
except:
    from urllib.request import urlretrieve
from .processors import *
from .sentiment import SentimentAnalysisAPI
from .odin import OdinAPI
import os
import shlex
import os
import subprocess as sp
import requests
import time
import sys
import logging


class ProcessorsAPI(object):

    PROC_VAR = 'PROCESSORS_SERVER'
    # save to lib loc
    DEFAULT_JAR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "processors-server.jar")
    #print(resource_filename(__name__, "processors-server.jar"))

    def __init__(self, port, hostname="localhost", timeout=120, jvm_mem="-Xmx3G", jar_path=None, keep_alive=False, log_file=None):

        self.hostname = hostname
        self.port = port
        self.make_address(hostname, port)
        self._start_command = "java {} -cp {} NLPServer --port {port} --host {host}" # mem, jar path, port, host
        self.timeout = timeout
        self.jvm_mem = jvm_mem
        # whether or not to stop the server when the object is destroyed
        self.keep_alive = keep_alive
        # how long to wait between requests
        self.wait_time = 2
        # processors
        self.default = Processor(self.address)
        self.fastnlp = FastNLPProcessor(self.address)
        self.bionlp = BioNLPProcessor(self.address)
        # sentiment
        self.sentiment = SentimentAnalysisAPI(self.address)
        # odin
        self.odin = OdinAPI(self.address)
        # use the os module's devnull for compatibility with python 2.7
        #self.DEVNULL = open(os.devnull, 'wb')
        self.logger = logging.getLogger(__name__)
        self.log_file = self.prepare_log_file(log_file)

        # resolve jar path
        self.resolve_jar_path(jar_path)
        # attempt to establish connection with server
        self.establish_connection()

    def prepare_log_file(self, lf):
        """
        Configure logger and return file path for logging
        """
        # log_file
        log_file = os.path.expanduser(os.path.join("~", ".py-processors.log")) if not lf else os.path.expanduser(lf)
        # configure logger
        self.logger.setLevel(logging.DEBUG)
        # create console handler and set level to info
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        # create debug file handler and set level to debug
        handler = logging.FileHandler(log_file, "w")
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        return log_file

    def annotate(self, text):
        """
        Uses default processor (CoreNLP) to annotate text.  Included for backwards compatibility.
        """
        return self.default.annotate(text)

    def annotate_from_sentences(self, sentences):
        """
        Uses default processor (CoreNLP) to annotate a list of segmented sentences.
        """
        return self.default.annotate_from_sentences(sentences)

    def establish_connection(self):
        """
        Attempt to connect to a server (assumes server is running)
        """
        if self.annotate("Blah"):
            print("Connection with server established!")
        else:
            try:
                # Attempt to start the server
                self._start_server()
            except Exception as e:
                if not os.path.exists(self.jar_path):
                    print("\nprocessors-server.jar not found at {}.".format(self.jar_path))
                print("Unable to start server. Please start the server manually with .start_server(\"path/to/processors-server.jar\")")
                print("\n{}".format(e))

    def resolve_jar_path(self, jar_path):
        """
        Attempts to preferentially set value of self.jar_path
        """
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
                    self.jar_path = None
                    print("WARNING: {0} path is invalid.  \nPlease verify this entry in your environment:\n\texport {0}=/path/to/processors-server.jar".format(ProcessorsAPI.PROC_VAR))
            # Preference 3: attempt to use the processors-sever.jar (download if not found)
            else:
                print("Using default")
                # check if jar exists
                if not os.path.exists(ProcessorsAPI.DEFAULT_JAR):
                    ProcessorsAPI.download_jar()
                self.jar_path = ProcessorsAPI.DEFAULT_JAR

    def start_server(self, jar_path=None, timeout=120):
        """
        Starts processors-sever.jar
        """
        self.timeout = int(float(timeout)/2)
        if jar_path:
            self.jar_path = jar_path
        self._start_server()

    def stop_server(self, port=None):
        """
        Sends a poison pill to the server and waits for shutdown response
        """
        port = port or self.port
        address = "http://{}:{}".format(self.hostname, port)
        shutdown_address = "{}/shutdown".format(address)
        # attempt shutdown
        try:
            response = requests.post(shutdown_address)
            if response:
                print(response.content.decode("utf-8"))
            return True
        # will fail if the server is already down
        except Exception as e:
            pass
        return False

    def _ensure_jar_path_exists(self):
        # check if jar exists
        if not os.path.exists(self.jar_path):
            raise Exception("jar not found at {}".format(self.jar_path))

    def _start_server(self, port=None):
        """
        "Private" method called by start_server()
        """

        self._ensure_jar_path_exists()

        if port:
            self.port = port
        # build the command
        cmd = self._start_command.format(self.jvm_mem, self.jar_path, port=self.port, host=self.hostname)
        self._process = sp.Popen(shlex.split(cmd),
                                 shell=False,
                                 stderr=open(self.log_file, 'wb'),
                                 stdout=open(self.log_file, 'wb'),
                                 universal_newlines=True)

        self.logger.info("Starting processors-server ({}) ...".format(cmd))
        print("\nWaiting for server...")

        progressbar_length = int(self.timeout/self.wait_time)
        for i in range(progressbar_length):
            try:
                success = self.annotate("blah")
                if success:
                    print("\n\nConnection with processors-server established ({})".format(self.address))
                    return True
                sys.stdout.write("\r[{:{}}]".format('='*i, progressbar_length))
                time.sleep(self.wait_time)
            except Exception as e:
                raise(e)

        # if the server still hasn't started, raise an Exception
        raise Exception("Couldn't connect to processors-server. Is the port in use?")

    def make_address(self, hostname, port):
        # update hostname
        self.hostname = hostname
        # update port
        self.port = port
        # update address
        self.address = "http://{}:{}".format(self.hostname, self.port)

    @staticmethod
    def download_jar(jar_url="http://www.cs.arizona.edu/~hahnpowell/processors-server/current/processors-server.jar"):
        # download processors-server.jar
        ppjar = ProcessorsAPI.DEFAULT_JAR
        percent = 0
        def dlProgress(count, blockSize, totalSize):
            percent = int(count*blockSize*100/totalSize)
            sys.stdout.write("\r{}% complete".format(percent))
            sys.stdout.flush()

        print("Downloading {} from {} ...".format(ppjar, jar_url))
        urlretrieve(jar_url, ppjar, reporthook=dlProgress)
        print("\nDownload Complete! {}".format(ppjar))


    def _get_path(self, p):
        """
        Expand a user-specified path.  Supports "~" shortcut.
        """
        return os.path.abspath(os.path.normpath(os.path.expanduser(p)))

    def __del__(self):
        """
        Stop server unless otherwise specified
        """
        if not self.keep_alive:
            try:
                self.stop_server()
                # close our file object
                #self.DEVNULL.close()
                print("Successfully shut down processors-server!")
            except Exception as e:
                self.logger.debug(e)
                print("Couldn't kill processors-server.  Was server started externally?")
