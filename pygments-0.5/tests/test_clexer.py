# -*- coding: utf-8 -*-
"""
    Basic CLexer Test
    ~~~~~~~~~~~~~~~~~

    :copyright: 2006 by Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""

import unittest
import os

from pygments.token import Text, Number
from pygments.lexers import CLexer


class CLexerTest(unittest.TestCase):

    def setUp(self):
        self.lexer = CLexer()

    def testNumbers(self):
        code = '42 23.42 23. .42 023 0xdeadbeef 23e+42 42e-23'
        wanted = []
        for item in zip([Number.Integer, Number.Float, Number.Float,
                         Number.Float, Number.Oct, Number.Hex,
                         Number.Float, Number.Float], code.split()):
            wanted.append(item)
            wanted.append((Text, ' '))
        wanted = [(Text, '')] + wanted[:-1] + [(Text, '\n')]
        self.assertEqual(list(self.lexer.get_tokens(code)), wanted)


if __name__ == '__main__':
    unittest.main()
