#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
parse markdown text to markdown object
"""

from dataclasses import dataclass, field
from enum import Enum
import logging
import re
from typing import List


LOGGER = logging.getLogger(__name__)


class ContentType(Enum):
    """
    Positble Content Type Enum
    """
    header1 = "#"
    header2 = "##"
    header3 = "###"
    header4 = "####"
    header5 = "#####"
    header6 = "######"
    chapter = "#*"
    default = "plain text"


@dataclass
class BaseObject:
    """
    All Markdown Object should inherit this Class
    """
    content: str  # plain text
    raw: str  # raw content
    content_type: ContentType = ContentType.default
    children: List["BaseObject"] = field(default_factory=list)

    @classmethod
    def is_token(cls, text, next_char) -> bool:
        """
        givin a text and the next_char,
        check if the text plus next_char is my type
        """
        raise NotImplementedError

    @classmethod
    def consume(cls, text: str) -> ("BaseObject", str):
        """
        consume the text and return the object and text unconsumed
        """
        raise NotImplementedError


@dataclass
class PlainText(BaseObject):
    """
    PlainText should match all kind of text
    """
    content_type = ContentType.default

    @classmethod
    def is_token(cls, text, next_char) -> bool:
        if re.match(r"\w+$", text):
            return True
        return False

    @staticmethod
    def consume(text: str) -> (BaseObject, str):
        line, text = text.split("\n", 1)
        return PlainText(line, raw=line+"\n"), text


@dataclass
class Header(BaseObject):
    """
    header, the level should be between 1 and 6
    """
    level: int = 1

    @staticmethod
    def is_token(text, next_char) -> bool:
        if re.match("#{1,6}$", text) and next_char == " ":
            return True
        return False

    @staticmethod
    def match(line: str) -> bool:
        if re.match("#{1,6} ", line):
            return True
        return False

    @classmethod
    def consume(cls, text) -> ("Header", str):
        LOGGER.debug("Header consume")
        header, text = text.split(" ", 1)
        content, text = text.split("\n", 1)
        level = len(header)
        LOGGER.debug("remain: %s", text)
        return Header(
            content_type=ContentType[f"header{level}"],
            content=content,
            raw="#" * level + " " + content + "\n",
        ), text

    @staticmethod
    def get_level(text) -> int:
        prefix = text.split(" ", 1)[0]
        assert re.match(r"#{1,6}$", prefix)
        return len(prefix)


@dataclass
class Chapter(BaseObject):
    """
    A chapter should contain a Header and remain children
    """
    header: Header = None
    content_type = ContentType.chapter

    @staticmethod
    def is_token(text, next_char) -> bool:
        return Header.is_token(text, next_char)

    @classmethod
    def consume(cls, text) -> ("Chapter", str):
        header, text = Header.consume(text)
        chapter = Chapter(
            header=header,
            content=header.content,
            raw=header.raw,
        )
        chapter_text = ""
        while text:
            line, text = text.split("\n", 1)
            if Header.match(line) and Header.get_level(line) <= header.level:
                text = line + "\n" + text
                break
            chapter_text += line + "\n"
        objects = parse(chapter_text)
        chapter.children = objects
        chapter.raw += "".join(
            child.raw
            for child in chapter.children
        )
        return chapter, text


PARSER = [
    Chapter,
    PlainText,
]


def parse(text: str) -> [BaseObject]:
    results = []
    if text and text[-1] != "\n":
        text += "\n"
    un_parsed_text = ""
    while text:
        un_parsed_text += text[0]
        text = text[1:]
        next_char = text[0]
        LOGGER.debug("try every parser_class to parse: %s.", un_parsed_text)
        for parser_class in PARSER:
            if parser_class.is_token(un_parsed_text, next_char):
                base_object, text = parser_class.consume(un_parsed_text + text)
                results.append(base_object)
                un_parsed_text = ""
                break
    return results
