# -*- coding: utf-8 -*-
"""
    pygments.util
    ~~~~~~~~~~~~~

    Utility functions.

    :copyright: 2006 by Georg Brandl.
    :license: GNU LGPL, see LICENSE for more details.
"""
import re


split_path_re = re.compile(r'[/\\ ]')
doctype_lookup_re = re.compile(r'''(?smx)
    (<\?.*?\?>)?\s*
    <!DOCTYPE\s+(
     [a-zA-Z_][a-zA-Z0-9]*\s+
     [a-zA-Z_][a-zA-Z0-9]*\s+
     "[^"]*")
     [^>]+>
''')
tag_re = re.compile(r'<(.+?)(\s.*?)?>.*?</\1>(?uism)')


class OptionError(Exception):
    pass


def get_bool_opt(options, optname, default=None):
    string = options.get(optname, default)
    if isinstance(string, bool):
        return string
    elif string.lower() in ('1', 'yes', 'true', 'on'):
        return True
    elif string.lower() in ('0', 'no', 'false', 'off'):
        return False
    else:
        raise OptionError('Invalid value %r for option %s; use '
                          '1/0, yes/no, true/false, on/off' %
                          string, optname)


def get_int_opt(options, optname, default=None):
    string = options.get(optname, default)
    try:
        return int(string)
    except ValueError:
        raise OptionError('Invalid value %r for option %s; you '
                          'must give an integer value' %
                          string, optname)


def get_list_opt(options, optname, default=None):
    val = options.get(optname, default)
    if isinstance(val, basestring):
        return val.split()
    elif isinstance(val, (list, tuple)):
        return list(val)
    else:
        raise OptionError('Invalid value %r for option %s; you '
                          'must give a list value' %
                          val, optname)


def make_analysator(f):
    """
    Return a static text analysation function that
    returns float values.
    """
    def text_analyse(text):
        rv = f(text)
        if not rv:
            return 0.0
        return min(1.0, max(0.0, float(rv)))
    text_analyse.__doc__ = f.__doc__
    return staticmethod(text_analyse)


def shebang_matches(text, regex):
    """
    Check if the given regular expression matches the last part of the
    shebang if one exists.

        >>> from pygments.util import shebang_matches
        >>> shebang_matches('#!/usr/bin/env python', r'python(2\.\d)?')
        True
        >>> shebang_matches('#!/usr/bin/python2.4', r'python(2\.\d)?')
        True
        >>> shebang_matches('#!/usr/bin/python-ruby', r'python(2\.\d)?')
        False
        >>> shebang_matches('#!/usr/bin/python/ruby', r'python(2\.\d)?')
        False
        >>> shebang_matches('#!/usr/bin/startsomethingwith python',
        ...                 r'python(2\.\d)?')
        True

    It also checks for common windows executable file extensions::

        >>> shebang_matches('#!C:\\Python2.4\\Python.exe', r'python(2\.\d)?')
        True

    Parameters (``'-f'`` or ``'--foo'`` are ignored so ``'perl'`` does
    the same as ``'perl -e'``)

    Note that this method automatically searches the whole string (eg:
    the regular expression is wrapped in ``'^$'``)
    """
    index = text.find('\n')
    if index >= 0:
        first_line = text[:index].lower()
    else:
        first_line = text.lower()
    if first_line.startswith('#!'):
        try:
            found = [x for x in split_path_re.split(first_line[2:].strip())
                     if x and not x.startswith('-')][-1]
        except IndexError:
            return False
        regex = re.compile('^%s(\.(exe|cmd|bat|bin))?$' % regex, re.IGNORECASE)
        if regex.search(found) is not None:
            return True
    return False


def doctype_matches(text, regex):
    """
    Check if the doctype matches a regular expression (if present).
    Note that this method only checks the first part of a DOCTYPE.
    eg: 'html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"'
    """
    m = doctype_lookup_re.match(text)
    if m is None:
        return False
    doctype = m.group(2)
    return re.compile(regex).match(doctype.strip()) is not None


def html_doctype_matches(text):
    """
    Check if the file looks like it has a html doctype
    """
    return doctype_matches(text, r'html\s+PUBLIC\s+"-//W3C//DTD X?HTML.*')


def looks_like_xml(text):
    """
    Check if a doctype exists or if we have some tags
    """
    m = doctype_lookup_re.match(text)
    if m is not None:
        return True
    return tag_re.search(text) is not None
