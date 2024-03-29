# -*- coding: utf-8 -*-
"""
    pygments.styles.autumn
    ~~~~~~~~~~~~~~~~~~~~~~

    A colorful style, inspired by the terminal highlighting style.

    :copyright: 2006 by Armin Ronacher.
    :license: GNU LGPL, see LICENSE for more details.
"""

from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic


class AutumnStyle(Style):

    default_style = ""

    styles = {
        Comment:                    "italic #aaaaaa",
        Comment.Preproc:            "noitalic #4c8317",

        Keyword:                    "#0000aa",
        Keyword.Type:               "#00aaaa",

        Operator.Word:              "#0000aa",

        Name.Builtin:               "#00aaaa",
        Name.Function:              "#00aa00",
        Name.Class:                 "underline #00aa00",
        Name.Namespace:             "underline #00aaaa",
        Name.Variable:              "#aa0000",
        Name.Constant:              "#aa0000",
        Name.Entity:                "bold #800",
        Name.Attribute:             "#1e90ff",
        Name.Tag:                   "bold #1e90ff",
        Name.Decorator:             "#888888",

        String:                     "#aa5500",
        String.Symbol:              "#0000aa",
        String.Regex:               "#009999",

        Number:                     "#009999",

        Generic.Heading:            "bold #000080",
        Generic.Subheading:         "bold #800080",
        Generic.Deleted:            "#aa0000",
        Generic.Inserted:           "#00aa00",
        Generic.Error:              "#aa0000",
        Generic.Emph:               "italic",
        Generic.Strong:             "bold",
        Generic.Prompt:             "#555555",
        Generic.Output:             "#888888",
        Generic.Traceback:          "#aa0000",

        Error:                      "#F00 bg:#FAA"
    }
