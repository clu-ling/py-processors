#!/usr/bin/env python
# -*- coding: utf-8 -*-

# __future__ import must be first
from __future__ import absolute_import
from .ds import *
from .odin import Mention
from .api import ProcessorsAPI
from .serialization import JSONSerializer
import json


__title__ = 'py-processors'
__version__ = '3.0.1'
__ps_rec__ = '3.0' # known compatible version of server
__author__ = 'Gus Hahn-Powell'
__copyright__ = 'Copyright 2016 Gus Hahn-Powell'
