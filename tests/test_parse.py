#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import unittest
from pathlib import Path
from markdown_ast import parse


ROOT = Path(__file__).parent / "input"


class TestHeader(unittest.TestCase):

    def test_header1(self):
        parse("# title")
        breakpoint()
