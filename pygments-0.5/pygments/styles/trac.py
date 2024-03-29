# -*- coding: utf-8 -*-
"""
    pygments.styles.trac
    ~~~~~~~~~~~~~~~~~~~~

    Port of the default trac highlighter design.

    :copyright: 2006 by Edgewall, Armin Ronacher.
    :license: GNU LGPL, see LICENSE for more details.
"""

from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic


class TracStyle(Style):

    default_style = ''

    styles = {
        Comment:                'italic #999988',
        Comment.Preproc:        'bold noitalic #999999',

        Operator:               'bold',

        String:                 '#bb8844',
        String.Regex:           '#808000',

        Number:                 '#009999',

        Keyword:                'bold',
        Keyword.Type:           '#445588',

        Name.Builtin:           '#999999',
        Name.Function:          'bold #990000',
        Name.Class:             'bold #445588',
        Name.Exception:         'bold #990000',
        Name.Namespace:         '#555555',
        Name.Variable:          '#ff99ff',
        Name.Constant:          '#ff99ff',
        Name.Tag:               '#000080',
        Name.Attribute:         '#008080',
        Name.Entity:            '#800080',

        Generic.Heading:        '#999999',
        Generic.Subheading:     '#aaaaaa',
        Generic.Deleted:        'bg:#ffdddd #000000',
        Generic.Inserted:       'bg:#ddffdd #000000',
        Generic.Error:          '#aa0000',
        Generic.Emph:           'italic',
        Generic.Strong:         'bold',
        Generic.Prompt:         '#555555',
        Generic.Output:         '#888888',
        Generic.Traceback:      '#aa0000',

        Error:                  'bg:#e3d2d2 #a61717'
    }
