# -*- coding: utf-8 -*-
"""
    pygments.lexers.special
    ~~~~~~~~~~~~~~~~~~~~~~~

    Special lexers.

    :copyright: 2006 by Georg Brandl.
    :license: GNU LGPL, see LICENSE for more details.
"""

import re
import cStringIO

from pygments.lexer import Lexer
from pygments.token import Token, Error, Text


__all__ = ['TextLexer', 'RawTokenLexer']


class TextLexer(Lexer):
    name = 'Text only'
    aliases = ['text']
    filenames = ['*.txt']
    mimetypes = ['text/plain']

    def get_tokens_unprocessed(self, text):
        yield 0, Text, text


_ttype_cache = {}

line_re = re.compile('.*?\n')

class RawTokenLexer(Lexer):
    """
    Recreate a token stream formatted with the RawTokenFormatter.

    Additional options accepted:

    ``compress``
        If set to "gz" or "bz2", decompress the token stream with
        the given compression algorithm (default: '').
    """
    name = 'Raw token data'
    aliases = ['raw']
    filenames = ['*.raw']
    mimetypes = ['application/x-pygments-tokens']

    def __init__(self, **options):
        self.compress = options.get('compress', '')
        Lexer.__init__(self, **options)

    def get_tokens(self, text):
        if self.compress == 'gz':
            import gzip
            gzipfile = gzip.GzipFile('', 'rb', 9, cStringIO.StringIO(text))
            text = gzipfile.read()
        elif self.compress == 'bz2':
            import bz2
            text = bz2.decompress(text)
        return Lexer.get_tokens(self, text)

    def get_tokens_unprocessed(self, text):
        length = 0
        for match in line_re.finditer(text):
            try:
                ttypestr, val = match.group().split('\t', 1)
            except ValueError:
                val = match.group()
                ttype = Error
            else:
                ttype = _ttype_cache.get(ttypestr)
                if not ttype:
                    ttype = Token
                    ttypes = ttypestr.split('.')[1:]
                    for ttype_ in ttypes:
                        ttype = getattr(ttype, ttype_)
                    _ttype_cache[ttypestr] = ttype
                val = val[1:-2].decode('string-escape')
            yield length, ttype, val
            length += len(val)
