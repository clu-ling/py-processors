#!/usr/bin/env python
# -*- coding: utf-8 -*-

# __future__ import must be first
from __future__ import absolute_import
from .ds import *
from .odin import Mention
from .api import ProcessorsBaseAPI, ProcessorsAPI
from .serialization import JSONSerializer
import json


__title__ = 'py-processors'
__version__ = '3.2.3'
__ps_rec__ = '3.2.0' # known compatible version of server
__author__ = 'Gus Hahn-Powell'
__copyright__ = 'Copyright 2015 Gus Hahn-Powell'

SERVER_JAR_URL = """http://py-processors.parsertongue.com/v{}/processors-server.jar""".format(__ps_rec__)
