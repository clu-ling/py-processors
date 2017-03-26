#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
import json
import os


def post_json(service, json_data):
    # POST json to the server API
    #response = requests.post(service, json={"text":"{}".format(text)})
    # for older versions of requests, use the call below
    #print("SERVICE: {}".format(service))
    response = requests.post(service,
                             data=json_data,
                             headers={'content-type': 'application/json; charset=utf-8'},
                             timeout=None
                             )
    # response content should be utf-8
    #response.encoding = "utf-8"
    content = response.content.decode("utf-8")
    #print("CONTENT: {}".format(content))
    return json.loads(content)

def full_path(p):
    """
    Expand a path.  Supports "~" shortcut.
    """
    return os.path.abspath(os.path.normpath(os.path.expanduser(p)))

class LabelManager(object):
    """
    Keep track of common labels
    """
    UNKNOWN = "UNKNOWN"
    # the O in IOB notation
    O = "O"
