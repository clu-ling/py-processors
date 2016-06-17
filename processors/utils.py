#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json

def post_json(service, json_data):
    # POST json to the server API
    #response = requests.post(service, json={"text":"{}".format(text)})
    # for older versions of requests, use the call below
    #print("SERVICE: {}".format(service))
    response = requests.post(service,
                             data=json_data,
                             headers={"content-type": "application/json"},
                             timeout=None
                             )
    # response content should be utf-8
    content = response.content.decode("utf-8")
    #print("CONTENT: {}".format(content))
    return json.loads(content)
