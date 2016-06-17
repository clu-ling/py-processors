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
import sys
import logging


class ProcessorsAPI(object):

    PROC_VAR = 'PROCESSORS_SERVER'

    def __init__(self, port, hostname="127.0.0.1", jar_path=None, log_file=None):

        self.hostname = hostname
        self.port = port
        self.make_address(hostname, port)
        self._start_command = "java -cp {} NLPServer {}"
        self.timeout = 120
        # how long to wait between requests
        self.wait_time = 2
        # processors
        self.default = Processor(self.address)
        self.fastnlp = FastNLPProcessor(self.address)
        self.bionlp = BioNLPProcessor(self.address)
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
        # attach handler
        handler = logging.FileHandler(log_file)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        return log_file

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

    def _start_server(self, port=None):
        """
        "Private" method called by start_server()
        """
        if port:
            self.port = port
        # build the command
        cmd = self._start_command.format(self.jar_path, self.port)
        #print(cmd)
        self._process = sp.Popen(shlex.split(cmd),
                                 shell=False,
                                 stderr=open(self.log_file, 'wb'),
                                 stdout=open(self.log_file, 'wb'),
                                 universal_newlines=True)

        print("Starting processors-server ({}) on port {} ...".format(self.jar_path, self.port))
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
            #self.DEVNULL.close()
            print("Successfully shut down processors-server!")
        except Exception as e:
            #print(e)
            print("Couldn't kill processors-server.  Was server started externally?")
