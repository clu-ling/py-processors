#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from itertools import count
from IPython.core.display import display, HTML
import os


class JupyterVisualizer(object):
    """
    Widgets for use with jupyter notebook
    """

    ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

    with open(os.path.join(ASSETS_DIR, "displacy-processors.js")) as js_file:
        dp_lib = js_file.read()
    with open(os.path.join(ASSETS_DIR, "displacy-processors.html")) as html_file:
        base_contents = html_file.read()
    with open(os.path.join(ASSETS_DIR, "displacy-processors.css")) as css_file:
        base_css = css_file.read()
    with open(os.path.join(ASSETS_DIR, "mentions.css")) as css_file:
        mentions_css = css_file.read()
    # style loosely corresponding to mention highlighting
    with open(os.path.join(ASSETS_DIR, "parse.css")) as css_file:
        parse_css = css_file.read()

    _id_gen = count(start=0, step=1)

    @staticmethod
    def graph_to_html(s, graph_name="stanford-collapsed", css=None, distance=None, div_id=None):
        distance = distance or int((sum(len(w) for w in s.words) + s.length) * 1.75)

        def next_id(): return next(JupyterVisualizer._id_gen)
        nid = next_id()
        div_id = div_id or "graph_{}".format(nid)

        # apply css only to current viz
        custom_css = css.replace(".displacy", "#{} .displacy".format(div_id)) if css else ""
        html = JupyterVisualizer.base_contents.format(
            dp_lib=JupyterVisualizer.dp_lib,
            dist=distance,
            sent_json=s.to_JSON(),
            div_id=div_id,
            css=custom_css,
            gn=graph_name
        )
        return html

    @staticmethod
    def display_graph(s, graph_name="stanford-collapsed", css=None, distance=None, div_id=None):
        res = JupyterVisualizer.graph_to_html(s=s, graph_name=graph_name, css=css, distance=distance, div_id=div_id)
        display(HTML(data=res))

    @staticmethod
    def mention_to_html(mention):
        SENTENCE_BOS = """<span class="sentence">"""
        MENTION_LABEL = """<sub class="mention-label">{}</sub>"""
        MENTION_SPAN_BOS = """<span class="mention-span sentence">"""
        ARG_BOS = """<span class="mention-arg mention-span sentence">"""
        TRIGGER_BOS = """<span class="mention-trigger mention-span sentence">"""
        EOS = "</span>"

        def add_label(label):
            return """<sup class="mention-role">{}</sup>""".format(label)

        def start_span(tag, w):
            return "{}{}".format(tag, w)
        def end_span(w, tag=""):
            return "{}{}{}".format(w,tag, EOS)

        sent = mention.sentenceObj
        sent_span = [w for w in sent.words]
        # mention trigger
        if mention.trigger:
            start = mention.trigger.start
            end = mention.trigger.end - 1
            sent_span[start] = start_span(TRIGGER_BOS, sent_span[start])
            sent_span[end] = end_span(sent_span[end],tag=add_label("TRIGGER"))
        # mention args
        if mention.arguments:
            for (role, args) in mention.arguments.items():
                for arg in args:
                    start  = arg.start
                    end = arg.end - 1
                    sent_span[start] = start_span(ARG_BOS + MENTION_LABEL.format(arg.label), sent_span[start])
                    sent_span[end] = end_span(sent_span[end], tag=add_label(role))
        # mention span
        start = mention.start
        end = mention.end - 1
        sent_span[start] = start_span(MENTION_SPAN_BOS + MENTION_LABEL.format(mention.label), sent_span[start])
        sent_span[end] = end_span(sent_span[end])
        # sentence tag
        start = 0
        end = -1
        sent_span[start] = start_span(SENTENCE_BOS, sent_span[start])
        sent_span[end] = end_span(sent_span[end])
        html = " ".join(sent_span)
        return """<style>{css}</style>{mention_html}""".format(css=JupyterVisualizer.mentions_css, mention_html=html)

    @staticmethod
    def display_mention(mention):
        res = JupyterVisualizer.mention_to_html(mention)
        display(HTML(res))
