#!/usr/bin/python3

import pytest
from argparse import Namespace

from docmanager import parsecli
from docmanager.action import Actions
from docmanager.core import DefaultDocManagerProperties
from docmanager.xmlhandler import XmlHandler

import shlex

def test_docmanager_init(tmp_valid_xml, capsys):
    """ Test the init sub command """

    # init without force
    clicmd = 'init {}'.format(tmp_valid_xml.strpath)
    a = Actions(parsecli(shlex.split(clicmd)))

    handler = XmlHandler(tmp_valid_xml.strpath)
    for i in DefaultDocManagerProperties:
        assert handler.is_prop_set(i) == True, "property {} is not set.".format(i)
