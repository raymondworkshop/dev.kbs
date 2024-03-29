# -*- coding: utf-8 -*-
"""
    pygments.lexer
    ~~~~~~~~~~~~~~

    Base lexer classes.

    :copyright: 2006 by Georg Brandl.
    :license: GNU LGPL, see LICENSE for more details.
"""
import re

try:
    set
except NameError:
    from sets import Set as set

from pygments.token import Error, Text, Other, _TokenType
from pygments.util import get_bool_opt, get_int_opt, make_analysator


__all__ = ['Lexer', 'RegexLexer', 'ExtendedRegexLexer', 'DelegatingLexer',
           'LexerContext', 'include', 'flags', 'bygroups', 'using', 'this']


_default_analyse = staticmethod(lambda x: 0.0)


class LexerMeta(type):
    """
    This metaclass automagically converts ``analyse_text`` methods into
    static methods which always return float values.
    """

    def __new__(cls, name, bases, d):
        if 'analyse_text' in d:
            d['analyse_text'] = make_analysator(d['analyse_text'])
        return type.__new__(cls, name, bases, d)


class Lexer(object):
    """
    Lexer for a specific language.

    Basic options recognized:
    ``stripnl``
        Strip leading and trailing newlines from the input (default: True).
    ``stripall``
        Strip all leading and trailing whitespace from the input
        (default: False).
    ``tabsize``
        If given and greater than 0, expand tabs in the input (default: 0).
    """

    #: Name of the lexer
    name = None

    #: Shortcuts for the lexer
    aliases = []

    #: fn match rules
    filenames = []

    #: fn alias filenames
    alias_filenames = []

    #: mime types
    mimetypes = []

    __metaclass__ = LexerMeta

    def __init__(self, **options):
        self.options = options
        self.stripnl = get_bool_opt(options, 'stripnl', True)
        self.stripall = get_bool_opt(options, 'stripall', False)
        self.tabsize = get_int_opt(options, 'tabsize', 0)

    def __repr__(self):
        if self.options:
            return '<pygments.lexers.%s with %r>' % (self.__class__.__name__,
                                                     self.options)
        else:
            return '<pygments.lexers.%s>' % self.__class__.__name__

    def analyse_text(text):
        """
        Has to return a float between ``0`` and ``1`` that indicates
        if a lexer wants to highlight this text. Used by ``guess_lexer``.
        If this method returns ``0`` it won't highlight it in any case, if
        it returns ``1`` highlighting with this lexer is guaranteed.

        The `LexerMeta` metaclass automatically wraps this function so
        that it works like a static method (no ``self`` or ``cls``
        parameter) and the return value is automatically converted to
        `float`. If the return value is an object that is boolean `False`
        it's the same as if the return values was ``0.0``.
        """

    def get_tokens(self, text):
        """
        Return an iterable of (tokentype, value) pairs generated from ``text``.

        Also preprocess the text, i.e. expand tabs and strip it if wanted.
        """
        text = type(text)('\n').join(text.splitlines())
        if self.stripall:
            text = text.strip()
        elif self.stripnl:
            text = text.strip('\n')
        if self.tabsize > 0:
            text = text.expandtabs(self.tabsize)
        if not text.endswith('\n'):
            text += '\n'

        for i, t, v in self.get_tokens_unprocessed(text):
            yield t, v

    def get_tokens_unprocessed(self, text):
        """
        Return an iterable of (tokentype, value) pairs.
        In subclasses, implement this method as a generator to
        maximize effectiveness.
        """
        raise NotImplementedError


class DelegatingLexer(Lexer):
    """
    This lexer takes two lexer as arguments. A root lexer and
    a language lexer. First everything is scanned using the language
    lexer, afterwards all ``Other`` tokens are lexed using the root
    lexer.

    The lexers from the ``template`` lexer package use this base lexer.
    """

    def __init__(self, _root_lexer, _language_lexer, _needle=Other, **options):
        self.root_lexer = _root_lexer(**options)
        self.language_lexer = _language_lexer(**options)
        self.needle = _needle
        Lexer.__init__(self, **options)

    def get_tokens_unprocessed(self, text):
        buffered = ''
        insertions = []
        lng_buffer = []
        for i, t, v in self.language_lexer.get_tokens_unprocessed(text):
            if t is self.needle:
                if lng_buffer:
                    insertions.append((len(buffered), lng_buffer))
                    lng_buffer = []
                buffered += v
            else:
                lng_buffer.append((i, t, v))
        if lng_buffer:
            insertions.append((len(buffered), lng_buffer))
        return do_insertions(insertions,
                             self.root_lexer.get_tokens_unprocessed(buffered))


#-------------------------------------------------------------------------------
# RegexLexer and ExtendedRegexLexer
#


class include(str):
    """
    Indicates that a state should include rules from another state.
    """
    pass


class combined(tuple):
    """
    Indicates a state combined from multiple states.
    """

    def __new__(cls, *args):
        return tuple.__new__(cls, args)

    def __init__(self, *args):
        tuple.__init__(self, args)


class _PseudoMatch(object):
    """
    A pseudo match object constructed from a string.
    """

    def __init__(self, start, text):
        self._text = text
        self._start = start

    def start(self, arg=None):
        return self._start

    def end(self, arg=None):
        return self._start + len(self._text)

    def group(self, arg=None):
        if arg:
            raise IndexError('No such group')
        return self._text

    def groups(self):
        return (self._text,)

    def groupdict(self):
        return {}


def bygroups(*args):
    """
    Callback that yields multiple actions for each group in the match.
    """
    def callback(lexer, match, ctx=None):
        for i, action in enumerate(args):
            if type(action) is _TokenType:
                data = match.group(i + 1)
                if data:
                    yield match.start(i + 1), action, data
            else:
                if ctx:
                    ctx.pos = match.start(i + 1)
                for item in action(lexer, _PseudoMatch(match.start(i + 1),
                                   match.group(i + 1)), ctx):
                    if item:
                        yield item
        if ctx:
            ctx.pos = match.end()
    return callback


class _This(object):
    """
    Special singleton used for indicating the caller class.
    Used by ``using``.
    """
this = _This()


def using(_other, **kwargs):
    """
    Callback that processes the match with a different lexer.

    The keyword arguments are forwarded to the lexer.
    """
    if _other is this:
        def callback(lexer, match, ctx=None):
            s = match.start()
            for i, t, v in lexer.get_tokens_unprocessed(match.group()):
                yield i + s, t, v
            if ctx:
                ctx.pos = match.end()
    else:
        def callback(lexer, match, ctx=None):
            # XXX: cache that somehow
            kwargs.update(lexer.options)
            lx = _other(**kwargs)

            s = match.start()
            for i, t, v in lx.get_tokens_unprocessed(match.group()):
                yield i + s, t, v
            if ctx:
                ctx.pos = match.end()
    return callback


class RegexLexerMeta(LexerMeta):
    """
    Metaclass for RegexLexer, creates the self._tokens attribute from
    self.tokens on the first instantiation.
    """

    def _process_state(cls, state):
        assert type(state) is str, "wrong state name %r" % state
        assert state[0] != '#', "invalid state name %r" % state
        if state in cls._tokens:
            return cls._tokens[state]
        tokens = cls._tokens[state] = []
        rflags = cls.flags
        for tdef in cls.tokens[state]:
            if isinstance(tdef, include):
                # it's a state reference
                assert tdef != state, "circular state reference %r" % state
                tokens.extend(cls._process_state(str(tdef)))
                continue

            assert type(tdef) is tuple, "wrong rule def %r" % tdef

            rex = re.compile(tdef[0], rflags)

            assert type(tdef[1]) is _TokenType or callable(tdef[1]), \
                   'token type must be simple type or callable, not %r' % tdef[1]

            if len(tdef) == 2:
                new_state = None
            else:
                tdef2 = tdef[2]
                if isinstance(tdef2, str):
                    # an existing state
                    if tdef2 == '#pop':
                        new_state = -1
                    elif tdef2 in cls.tokens:
                        new_state = (tdef2,)
                    elif tdef2 == '#push':
                        new_state = tdef2
                    elif tdef2[:5] == '#pop:':
                        new_state = -int(tdef2[5:])
                    else:
                        assert False, 'unknown new state %r' % tdef2
                elif isinstance(tdef2, combined):
                    # combine a new state from existing ones
                    new_state = '_tmp_%d' % cls._tmpname
                    cls._tmpname += 1
                    itokens = []
                    for istate in tdef2:
                        assert istate != state, 'circular state ref %r' % istate
                        itokens.extend(cls._process_state(istate))
                    cls._tokens[new_state] = itokens
                    new_state = (new_state,)
                elif isinstance(tdef2, tuple):
                    # push more than one state
                    for state in tdef2:
                        assert state in cls.tokens, \
                               'unknown new state ' + state
                    new_state = tdef2
                else:
                    assert False, 'unknown new state def %r' % tdef2
            tokens.append((rex, tdef[1], new_state))
        return tokens

    def __call__(cls, *args, **kwds):
        if not hasattr(cls, '_tokens'):
            cls._tokens = {}
            cls._tmpname = 0
            for state in cls.tokens.keys():
                cls._process_state(state)

        return type.__call__(cls, *args, **kwds)


class RegexLexer(Lexer):
    """
    Base for simple stateful regular expression-based lexers.
    Simplifies the lexing process so that you need only
    provide a list of states and regular expressions.
    """
    __metaclass__ = RegexLexerMeta

    #: Flags for compiling the regular expressions.
    #: Defaults to MULTILINE.
    flags = re.MULTILINE

    #: Dict of ``{'state': [(regex, tokentype, new_state), ...], ...}``
    #:
    #: The initial state is 'root'.
    #: ``new_state`` can be omitted to signify no state transition.
    #: If it is a string, the state is pushed on the stack and changed.
    #: If it is a tuple of strings, all states are pushed on the stack and
    #: the current state will be the topmost.
    #: It can also be ``combined('state1', 'state2', ...)``
    #: to signify a new, anonymous state combined from the rules of two
    #: or more existing ones.
    #: Furthermore, it can be '#pop' to signify going back one step in
    #: the state stack, or '#push' to push the current state on the stack
    #: again.
    #:
    #: The tuple can also be replaced with ``include('state')``, in which
    #: case the rules from the state named by the string are included in the
    #: current one.
    tokens = {}

    def get_tokens_unprocessed(self, text, stack=('root',)):
        """
        Split ``text`` into (tokentype, text) pairs.

        ``stack`` is the inital stack (default: ``['root']``)
        """
        pos = 0
        statestack = list(stack)
        statetokens = self._tokens[statestack[-1]]
        while 1:
            for rex, action, new_state in statetokens:
                m = rex.match(text, pos)
                if m:
                    if type(action) is _TokenType:
                        yield pos, action, m.group()
                    else:
                        for item in action(self, m):
                            yield item
                    pos = m.end()
                    if new_state is not None:
                        # state transition
                        if isinstance(new_state, tuple):
                            statestack.extend(new_state)
                        elif isinstance(new_state, int):
                            # pop
                            del statestack[new_state:]
                        elif new_state == '#push':
                            statestack.append(statestack[-1])
                        else:
                            assert False, "wrong state def: %r" % new_state
                        statetokens = self._tokens[statestack[-1]]
                    break
            else:
                try:
                    if text[pos] == '\n':
                        # at EOL, reset state to "root"
                        pos += 1
                        statestack = ['root']
                        statetokens = self._tokens['root']
                        yield pos, Text, '\n'
                        continue
                    yield pos, Error, text[pos]
                    pos += 1
                except IndexError:
                    break


class LexerContext(object):
    """
    A helper object that holds lexer position data.
    """

    def __init__(self, text, pos, stack=None, end=None):
        self.text = text
        self.pos = pos
        self.end = end or len(text) # end=0 not supported ;-)
        self.stack = stack or ['root']

    def __repr__(self):
        return 'LexerContext(%r, %r, %r)' % (
            self.text, self.pos, self.stack)


class ExtendedRegexLexer(RegexLexer):
    """
    A RegexLexer that uses a context object to store its state.
    """

    def get_tokens_unprocessed(self, text=None, context=None):
        """
        Split ``text`` into (tokentype, text) pairs.
        If ``context`` is given, use this lexer context instead.
        """
        if not context:
            ctx = LexerContext(text, 0)
            statetokens = self._tokens['root']
        else:
            ctx = context
            statetokens = self._tokens[ctx.stack[-1]]
            text = ctx.text
        while 1:
            for rex, action, new_state in statetokens:
                m = rex.match(text, ctx.pos, ctx.end)
                if m:
                    if type(action) is _TokenType:
                        yield ctx.pos, action, m.group()
                        ctx.pos = m.end()
                    else:
                        for item in action(self, m, ctx):
                            yield item
                        if not new_state:
                            # altered the state stack?
                            statetokens = self._tokens[ctx.stack[-1]]
                    # CAUTION: callback must set ctx.pos!
                    if new_state is not None:
                        # state transition
                        if isinstance(new_state, tuple):
                            ctx.stack.extend(new_state)
                        elif isinstance(new_state, int):
                            # pop
                            del ctx.stack[new_state:]
                        elif new_state == '#push':
                            ctx.stack.append(ctx.stack[-1])
                        else:
                            assert False, "wrong state def: %r" % new_state
                        statetokens = self._tokens[ctx.stack[-1]]
                    break
            else:
                try:
                    if ctx.pos >= ctx.end:
                        break
                    if text[ctx.pos] == '\n':
                        # at EOL, reset state to "root"
                        ctx.pos += 1
                        ctx.stack = ['root']
                        statetokens = self._tokens['root']
                        yield ctx.pos, Text, '\n'
                        continue
                    yield ctx.pos, Error, text[ctx.pos]
                    ctx.pos += 1
                except IndexError:
                    break


def do_insertions(insertions, tokens):
    """
    Helper for lexers which must combine the results of several
    sublexers.

    ``insertions`` is a list of ``(index, itokens)`` pairs.
    Each ``itokens`` iterable should be inserted at position
    ``index`` into the token stream given by the ``tokens``
    argument.

    The result is a combined token stream.

    XXX: The indices yielded by this function are not correct!
    """
    insertions = iter(insertions)
    try:
        index, itokens = insertions.next()
    except StopIteration:
        # no insertions
        for item in tokens:
            yield item
        return

    insleft = True
    for i, t, v in tokens:
        oldi = 0
        while insleft and i + len(v) >= index:
            yield i, t, v[oldi:index-i]
            for item in itokens:
                yield item
            oldi = index-i
            try:
                index, itokens = insertions.next()
            except StopIteration:
                insleft = False
                break  # not strictly necessary
        yield i, t, v[oldi:]
