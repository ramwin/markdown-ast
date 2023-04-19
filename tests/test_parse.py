#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
unittest
"""


import logging
import unittest
from pathlib import Path
from markdown_ast import parse
from markdown_ast.obj import Header, ContentType


ROOT = Path(__file__).parent / "input"
logging.basicConfig(
    level=logging.DEBUG,
    format=(
        "%(asctime)s [%(pathname)s:%(lineno)d] %(message)s"
    ),
)


class TestExtreme(unittest.TestCase):

    def test_empty(self):
        a = parse("")
        self.assertEqual(a, [])


class TestHeader(unittest.TestCase):
    """test header parser"""

    @staticmethod
    def open(filename):
        with open(ROOT / filename) as f:
            return f.read()

    def test_header1(self):
        result = parse("# title")
        target = Header(
            content_type=ContentType.header1,
            content="title",
            raw="# title\n",
            level=1,
        )
        self.assertEqual(
            result[0].header,
            target,
        )

    def test_header_12(self):
        result = parse("# title\n# title2")
        target = Header(
            content_type=ContentType.header1,
            content="title2",
            raw="# title2\n",
            level=1,
        )
        self.assertEqual(
            result[1].header,
            target,
        )

    def test_nest_header(self):
        result = parse("# title\n## title2")
