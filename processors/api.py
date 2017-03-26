#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#from pkg_resources import resource_filename
from six.moves.urllib.request import urlretrieve
from .utils import *
from .annotators import *
from .sentiment import SentimentAnalysisAPI
from .serialization import JSONSerializer
import os
import shlex
import subprocess as sp
import requests
import re
import time
import sys
import logging
import warnings


class ProcessorsAPI(object):

    """
    Manages a connection with the processors-server jar and provides an interface to the API.

    Parameters
    ----------
    port : int
        The port the server is running on or should be started on.  Default is 8886.
    hostname : str
        The host name to use for the server.  Default is "localhost".
    timeout : int
        The number of seconds to wait for the server to initialize.  Default is 120.
    jvm_mem : str
        The maximum amount of memory to allocate to the JVM for the server.  Default is "-Xmx3G".
    jar_path : str
        The path to the processors-server jar.  Default is the jar installed with the package.
    kee_alive : bool
        Whether or not to keep the server running when ProcessorsAPI instance goes out of scope.  Default is false (server is shut down).
    log_file: str
        The path for the log file.  Default is .py-processors.log in the user's home directory.

    Methods
    -------
    annotate(text)
        Produces a Document from the provided `text` using the default processor.
    fastnlp.annotate(text)
        Produces a Document from the provided `text` using FastNLPProcessor.
    bionlp.annotate(text)
        Produces a Document from the provided `text` using BioNLPProcessor.
    annotate_from_sentences(sentences)
        Produces a Document from `sentences` (a list of text split into sentences). Uses the default processor.
    fastnlp.annotate_from_sentences(sentences)
        Produces a Document from `sentences` (a list of text split into sentences). Uses FastNLPProcessor.
    bionlp.annotate_from_sentences(sentences)
        Produces a Document from `sentences` (a list of text split into sentences). Uses BioNLPProcessor.
    corenlp.sentiment.score_sentence(sentence)
        Produces a sentiment score for the provided `sentence` (an instance of Sentence).
    corenlp.sentiment.score_document(doc)
        Produces sentiment scores for the provided `doc` (an instance of Document).  One score is produced for each sentence.
    corenlp.sentiment.score_segmented_text(sentences)
        Produces sentiment scores for the provided `sentences` (a list of text segmented into sentences).  One score is produced for item in `sentences`.
    odin.extract_from_text(text, rules)
        Produces a list of Mentions for matches of the provided `rules` on the `text`.  `rules` can be a string of Odin rules, or a url ending in `.yml` or `.yaml`.
    odin.extract_from_document(doc, rules)
        Produces a list of Mentions for matches of the provided `rules` on the `doc` (an instance of Document).  `rules` can be a string of Odin rules, or a url ending in .yml or yaml.
    start_server(jar_path, **kwargs)
        Starts the server using the provided `jar_path`.  Optionally takes hostname, port, jvm_mem, and timeout.
    stop_server()
        Attempts to stop the server running at self.address.
    """

    PROC_VAR = 'PROCESSORS_SERVER'
    TIMEOUT = 120
    # save to lib loc
    DEFAULT_JAR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "processors-server.jar")
    PORT = 8886
    JVM_MEM = "-Xmx3G"
    HOST = "localhost"
    LOG = full_path(os.path.join("~", "py-processors.log"))
    #print(resource_filename(__name__, "processors-server.jar"))

    def __init__(self, **kwargs):

        self.hostname = kwargs.get("hostname", ProcessorsAPI.HOST)
        self.port = kwargs.get("port", ProcessorsAPI.PORT)
        self.make_address(self.hostname, self.port)
        self.timeout = kwargs.get("timeout", ProcessorsAPI.TIMEOUT)
        self.jvm_mem = kwargs.get("jvm_mem", ProcessorsAPI.JVM_MEM)
        self._start_command = "java {mem} -cp {jp} NLPServer --port {port} --host {host}" # mem, jar path, port, host
        # whether or not to stop the server when the object is destroyed
        self.keep_alive = kwargs.get("keep_alive", False)
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
        self.log_file = self._prepare_log_file(kwargs.get("log_file", ProcessorsAPI.LOG))
        self.jar_path = kwargs.get("jar_path", ProcessorsAPI.DEFAULT_JAR)
        # attempt to establish connection with server
        self.establish_connection()

    def _check_server_version(self):
        """
        Checks server version to see if it meets the recommendations
        """
        # avoid circular imports by delaying this import
        from .__init__ import __ps_rec__
        try:
            service_address = "{}/version".format(self.address)
            server_version = post_json(service_address, None)["version"]
            if float(__ps_rec__) != float(server_version):
                warnings.warn("Recommended server version is {}, but server version is {}".format(__ps_rec__, server_version))
            else:
                self.logger.info("Server version meets recommendations (v{})".format(__ps_rec__))
        except:
            warnings.warn("Unable to determine server version.  Recommended version is {}".format(__ps_rec__))


    def _prepare_log_file(self, lf):
        """
        Configure logger and return file path for logging
        """
        # log_file
        log_file = ProcessorsAPI.LOG if not lf else os.path.expanduser(lf)
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

    def is_running(self):
        return True if self.annotate("Blah") else False

    def establish_connection(self):
        """
        Attempt to connect to a server (assumes server is running)
        """
        if self.is_running():
            self.logger.info("Connection with server established!")
            self._check_server_version()
        else:
            try:
                # resolve jar path if server is not already running
                self._resolve_jar_path(self.jar_path)
                # Attempt to start the server
                self._start_server()
            except Exception as e:
                self.logger.warn("Unable to start server. Please start the server manually with .start_server(jar_path=\"path/to/processors-server.jar\")")
                self.logger.warn("\n{}".format(e))

    def _resolve_jar_path(self, jar_path=None):
        """
        Attempts to preferentially set value of self.jar_path
        """
        # Preference 1: if a .jar is given, check to see if the path is valid
        if jar_path:
            jp = full_path(jar_path)
            # check if path is valid
            if os.path.exists(jp):
                self.jar_path = jp
        # Preference 2: if a PROCESSORS_SERVER environment variable is defined, check its validity
        elif ProcessorsAPI.PROC_VAR in os.environ:
            self.logger.info("Using path given via $PROCESSORS_SERVER")
            jp = full_path(os.environ[ProcessorsAPI.PROC_VAR])
            # check if path is valid
            if os.path.exists(jp):
                self.jar_path = jp
            else:
                self.jar_path = None
                self.logger.warn("WARNING: {0} path is invalid.  \nPlease verify this entry in your environment:\n\texport {0}=/path/to/processors-server.jar".format(ProcessorsAPI.PROC_VAR))
        # Preference 3: attempt to use the processors-sever.jar (download if not found)
        # check if jar exists
        if not self.jar_path or not os.path.exists(self.jar_path):
            self.logger.info("No jar found.  Downloading to {} ...".format(ProcessorsAPI.DEFAULT_JAR))
            ProcessorsAPI._download_jar()
            self.jar_path = ProcessorsAPI.DEFAULT_JAR

    def start_server(self, jar_path, **kwargs):
        """
        Starts processors-sever.jar
        """
        self.port = kwargs.get("port", self.port)
        self.hostname = kwargs.get("hostname", self.hostname)
        self.jvm_mem = kwargs.get("jvm_mem", self.jvm_mem)
        self.timeout = int(float(kwargs.get("timeout", self.jvm_mem))/2)
        jp = full_path(jar_path)
        if jp:
            self.jar_path = jp
            self._start_server()
        else:
            raise Exception("Please provide jar_path=\"path/to/processors-server.jar\"")

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

        # does the jar exist?
        self._ensure_jar_path_exists()

        if port:
            self.port = port
        # build the command
        cmd = self._start_command.format(mem=self.jvm_mem, jp=self.jar_path, port=self.port, host=self.hostname)
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
    def _download_jar(jar_url="http://www.cs.arizona.edu/~hahnpowell/processors-server/current/processors-server.jar"):
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


class OdinAPI(object):
    """
    API for performing rule-based information extraction with Odin.

    Parameters
    ----------
    address : str
        The base address for the API (i.e., everything preceding `/api/..`)

    """

    validator = re.compile("^(https?|ftp):.+?\.?ya?ml$")

    def __init__(self, address):
        self._service = "{}/api/odin/extract".format(address)

    def _extract(self, json_data):
        try:
            mns_json = post_json(self._service, json_data)
            return JSONSerializer.mentions_from_JSON(mns_json)
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def valid_rule_url(url):
        return True if OdinAPI.validator.match(url) else False

    def extract_from_text(self, text, rules):
        """
        Sends text to the server with rules for information extraction (IE).

        Parameters
        ----------
        text : str
            `rules` will be applied to this `text`.
        rules : str
            Either Odin rules provided as a `yaml` string, or a url pointing to a `yaml` file of rules.

        Returns
        -------
        [processors.odin.Mention] or None
            Rule matches produce a list of `processors.odin.Mention`.
        """
        if OdinAPI.valid_rule_url(rules):
            # this is actually a URL to a yaml file
            url = rules
            container = TextWithURL(text, url)
        else:
            container = TextWithRules(text, rules)
        return self._extract(container.to_JSON())

    def extract_from_document(self, doc, rules):
        """
        Sends a `processors.ds.Document` (`doc`) to the server with rules for information extraction (IE).

        Parameters
        ----------
        doc : processors.ds.Document
            `rules` will be applied to this `processors.ds.Document`.
        rules : str
            Either Odin rules provided as a `yaml` string, or a url pointing to a `yaml` file of rules.

        Returns
        -------
        [processors.odin.Mention] or None
            Rule matches produce a list of `processors.odin.Mention`.

        """
        if OdinAPI.valid_rule_url(rules):
            # this is actually a URL to a yaml file
            url = rules
            container = DocumentWithURL(doc, rules)
        else:
            container = DocumentWithRules(doc, rules)
        return self._extract(container.to_JSON())

#############################################
# Containers for Odin data
# transmitted to the server for processing
#############################################

class TextWithRules(object):

    def __init__(self, text, rules):
        self.text = text
        self.rules = rules

    def to_JSON_dict(self):
        jdict = dict()
        jdict["text"] = self.text
        jdict["rules"] = self.rules
        return jdict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)

class TextWithURL(object):

    def __init__(self, text, url):
        self.text = text
        # TODO: throw exception if url is invalid
        self.url = url

    def to_JSON_dict(self):
        jdict = dict()
        jdict["text"] = self.text
        jdict["url"] = self.url
        return jdict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)

class DocumentWithRules(object):

    def __init__(self, document, rules):
        # TODO: throw exception if isinstance(document, Document) is False
        self.document = document
        self.rules = rules

    def to_JSON_dict(self):
        jdict = dict()
        jdict["document"] = self.document.to_JSON_dict()
        jdict["rules"] = self.rules
        return jdict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)

class DocumentWithURL(object):

    def __init__(self, document, url):
        # TODO: throw exception if isinstance(document, Document) is False
        self.document = document
        # TODO: throw exception if url is invalid
        self.url = url

    def to_JSON_dict(self):
        jdict = dict()
        jdict["document"] = self.document.to_JSON_dict()
        jdict["url"] = self.url
        return jdict

    def to_JSON(self):
        return json.dumps(self.to_JSON_dict(), sort_keys=True, indent=4)
