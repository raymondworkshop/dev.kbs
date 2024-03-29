# -*- coding: utf-8 -*-
"""
    pygments.lexers.web
    ~~~~~~~~~~~~~~~~~~~

    Lexers for web-related languages: JavaScript, CSS, HTML, XML, PHP.

    :copyright: 2006 by Georg Brandl, Armin Ronacher.
    :license: GNU LGPL, see LICENSE for more details.
"""

import re
try:
    set
except NameError:
    from sets import Set as set

from pygments.lexer import Lexer, RegexLexer, bygroups, using
from pygments.token import \
     Text, Comment, Operator, Keyword, Name, String, Number, Other
from pygments.util import get_bool_opt, get_list_opt, looks_like_xml, \
                          html_doctype_matches


__all__ = ['HtmlLexer', 'XmlLexer', 'JavascriptLexer', 'CssLexer',
           'PhpLexer']


class JavascriptLexer(RegexLexer):
    name = 'JavaScript'
    aliases = ['js', 'javascript']
    filenames = ['*.js']
    mimetypes = ['application/x-javascript', 'text/x-javascript']

    flags = re.DOTALL
    tokens = {
        'root': [
            (r'\s+', Text),
            (r'//.*?\n', Comment),
            (r'/\*.*?\*/', Comment),
            (r'/(\\\\|\\/|[^/\n])*/[gim]*', String.Regex),
            (r'[~\^\*!%&\[\]\{\}\(\)<>\|+=:;,./?-]', Operator),
            (r'(for|in|while|do|break|return|continue|if|else|throw|try|'
             r'catch|var|with|const|label|function|new|typeof|'
             r'instanceof|this)\b', Keyword),
            (r'(true|false|null|NaN|Infinity|undefined)\b', Keyword.Constant),
            (r'(Array|Boolean|Date|Error|Function|Math|netscape|'
             r'Number|Object|Packages|RegExp|String|sun|decodeURI|'
             r'decodeURIComponent|encodeURI|encodeURIComponent|'
             r'Error|eval|isFinite|isNaN|parseFloat|parseInt|document|this|'
             r'window)\b', Name.Builtin),
            (r'[$a-zA-Z_][a-zA-Z0-9_]*', Name.Other),
            (r'[0-9]+', Number),
            (r'"(\\\\|\\"|[^"])*"', String.Double),
            (r"'(\\\\|\\'|[^'])*'", String.Single),
        ]
    }


class CssLexer(RegexLexer):
    name = 'CSS'
    aliases = ['css']
    filenames = ['*.css']
    mimetypes = ['text/css']

    tokens = {
        'root': [
            (r'\s+', Text),
            (r'/\*(?:.|\n)*?\*/', Comment),
            (r'{', Operator, 'content'),
            (r'\:[a-zA-Z0-9_-]+', Name.Decorator),
            (r'\.[a-zA-Z0-9_-]+', Name.Class),
            (r'\#[a-zA-Z0-9_-]+', Name.Function),
            (r'[a-zA-Z0-9_-]+', Name.Tag),
            (r'[~\^\*!%&\[\]\(\)<>\|+=@:;,./?-]', Operator),
            (r'"(\\\\|\\"|[^"])*"', String.Double),
            (r"'(\\\\|\\'|[^'])*'", String.Single)
        ],
        'content': [
            (r'\s+', Text),
            (r'}', Operator, '#pop'),
            (r'url\(.*?\)', String.Other),
            (r'^@.*?$', Comment.Preproc),
            (r'(azimuth|background-attachment|background-color|'
             r'background-image|background-position|background-repeat|'
             r'background|border-bottom-color|border-bottom-style|'
             r'border-bottom-width|border-left-color|border-left-style|'
             r'border-left-width|border-right|border-right-color|'
             r'border-right-style|border-right-width|border-top-color|'
             r'border-top-style|border-top-width|border-bottom|'
             r'border-collapse|border-left|border-width|border-color|'
             r'border-spacing|border-style|border-top|border|caption-side|'
             r'clear|clip|color|content|counter-increment|counter-reset|'
             r'cue-after|cue-before|cue|cursor|direction|display|'
             r'elevation|empty-cells|float|font-family|font-size|'
             r'font-size-adjust|font-stretch|font-style|font-variant|'
             r'font-weight|font|height|letter-spacing|line-height|'
             r'list-style-type|list-style-image|list-style-position|'
             r'list-style|margin-bottom|margin-left|margin-right|'
             r'margin-top|margin|marker-offset|marks|max-height|max-width|'
             r'min-height|min-width|opacity|orphans|outline|outline-color|'
             r'outline-style|outline-width|overflow|padding-bottom|'
             r'padding-left|padding-right|padding-top|padding|page|'
             r'page-break-after|page-break-before|page-break-inside|'
             r'pause-after|pause-before|pause|pitch|pitch-range|'
             r'play-during|position|quotes|richness|right|size|'
             r'speak-header|speak-numeral|speak-punctuation|speak|'
             r'speech-rate|stress|table-layout|text-align|text-decoration|'
             r'text-indent|text-shadow|text-transform|top|unicode-bidi|'
             r'vertical-align|visibility|voice-family|volume|white-space|'
             r'widows|width|word-spacing|z-index|bottom|left|'
             r'above|absolute|always|armenian|aural|auto|avoid|baseline|'
             r'behind|below|bidi-override|blink|block|bold|bolder|both|'
             r'capitalize|center-left|center-right|center|circle|'
             r'cjk-ideographic|close-quote|collapse|condensed|continuous|'
             r'crop|crosshair|cross|cursive|dashed|decimal-leading-zero|'
             r'decimal|default|digits|disc|dotted|double|e-resize|embed|'
             r'extra-condensed|extra-expanded|expanded|fantasy|far-left|'
             r'far-right|faster|fast|fixed|georgian|groove|hebrew|help|'
             r'hidden|hide|higher|high|hiragana-iroha|hiragana|icon|'
             r'inherit|inline-table|inline|inset|inside|invert|italic|'
             r'justify|katakana-iroha|katakana|landscape|larger|large|'
             r'left-side|leftwards|level|lighter|line-through|list-item|'
             r'loud|lower-alpha|lower-greek|lower-roman|lowercase|ltr|'
             r'lower|low|medium|message-box|middle|mix|monospace|'
             r'n-resize|narrower|ne-resize|no-close-quote|no-open-quote|'
             r'no-repeat|none|normal|nowrap|nw-resize|oblique|once|'
             r'open-quote|outset|outside|overline|pointer|portrait|px|'
             r'relative|repeat-x|repeat-y|repeat|rgb|ridge|right-side|'
             r'rightwards|s-resize|sans-serif|scroll|se-resize|'
             r'semi-condensed|semi-expanded|separate|serif|show|silent|'
             r'slow|slower|small-caps|small-caption|smaller|soft|solid|'
             r'spell-out|square|static|status-bar|super|sw-resize|'
             r'table-caption|table-cell|table-column|table-column-group|'
             r'table-footer-group|table-header-group|table-row|'
             r'table-row-group|text|text-bottom|text-top|thick|thin|'
             r'transparent|ultra-condensed|ultra-expanded|underline|'
             r'upper-alpha|upper-latin|upper-roman|uppercase|url|'
             r'visible|w-resize|wait|wider|x-fast|x-high|x-large|x-loud|'
             r'x-low|x-small|x-soft|xx-large|xx-small|yes)\b', Keyword),
            (r'(indigo|gold|firebrick|indianred|yellow|darkolivegreen|'
             r'darkseagreen|mediumvioletred|mediumorchid|chartreuse|'
             r'mediumslateblue|black|springgreen|crimson|lightsalmon|brown|'
             r'turquoise|olivedrab|cyan|silver|skyblue|gray|darkturquoise|'
             r'goldenrod|darkgreen|darkviolet|darkgray|lightpink|teal|'
             r'darkmagenta|lightgoldenrodyellow|lavender|yellowgreen|thistle|'
             r'violet|navy|orchid|blue|ghostwhite|honeydew|cornflowerblue|'
             r'darkblue|darkkhaki|mediumpurple|cornsilk|red|bisque|slategray|'
             r'darkcyan|khaki|wheat|deepskyblue|darkred|steelblue|aliceblue|'
             r'gainsboro|mediumturquoise|floralwhite|coral|purple|lightgrey|'
             r'lightcyan|darksalmon|beige|azure|lightsteelblue|oldlace|'
             r'greenyellow|royalblue|lightseagreen|mistyrose|sienna|'
             r'lightcoral|orangered|navajowhite|lime|palegreen|burlywood|'
             r'seashell|mediumspringgreen|fuchsia|papayawhip|blanchedalmond|'
             r'peru|aquamarine|white|darkslategray|ivory|dodgerblue|'
             r'lemonchiffon|chocolate|orange|forestgreen|slateblue|olive|'
             r'mintcream|antiquewhite|darkorange|cadetblue|moccasin|'
             r'limegreen|saddlebrown|darkslateblue|lightskyblue|deeppink|'
             r'plum|aqua|darkgoldenrod|maroon|sandybrown|magenta|tan|'
             r'rosybrown|pink|lightblue|palevioletred|mediumseagreen|'
             r'dimgray|powderblue|seagreen|snow|mediumblue|midnightblue|'
             r'paleturquoise|palegoldenrod|whitesmoke|darkorchid|salmon|'
             r'lightslategray|lawngreen|lightgreen|tomato|hotpink|'
             r'lightyellow|lavenderblush|linen|mediumaquamarine|green|'
             r'blueviolet|peachpuff)\b', Name.Builtin),
            (r'\!important', Comment.Preproc),
            (r'/\*(?:.|\n)*?\*/', Comment),
            (r'\#[a-zA-Z0-9]{1,6}', Number),
            (r'[\.-]?[0-9]*[\.]?[0-9]+(em|px|\%|pt|pc|in|mm|cm|ex)', Number),
            (r'-?[0-9]+', Number),
            (r'[~\^\*!%&\[\]\(\)<>\|+=@:;,./?-]', Operator),
            (r'"(\\\\|\\"|[^"])*"', String.Double),
            (r"'(\\\\|\\'|[^'])*'", String.Single),
            (r'[a-zA-Z][a-zA-Z0-9]+', Name)
        ]
    }


class HtmlLexer(RegexLexer):
    name = 'HTML'
    aliases = ['html']
    filenames = ['*.html', '*.htm', '*.xhtml']
    mimetypes = ['text/html', 'application/xhtml+xml']

    flags = re.IGNORECASE | re.DOTALL
    tokens = {
        'root': [
            ('[^<&]+', Text),
            ('&.*?;', Name.Entity),
            (r'\<\!\[CDATA\[.*?\]\]\>', Comment.Preproc),
            ('<!--', Comment, 'comment'),
            (r'<\?.*?\?>', Comment.Preproc),
            ('<![^>]*>', Comment.Preproc),
            (r'<\s*script\s*', Name.Tag, ('script-content', 'tag')),
            (r'<\s*style\s*', Name.Tag, ('style-content', 'tag')),
            (r'<\s*[a-zA-Z0-9:]+', Name.Tag, 'tag'),
            (r'<\s*/\s*[a-zA-Z0-9:]+\s*>', Name.Tag),
        ],
        'comment': [
            ('[^-]+', Comment),
            ('-->', Comment, '#pop'),
            ('-', Comment),
        ],
        'tag': [
            (r'\s+', Text),
            (r'[a-zA-Z0-9_:-]+\s*=', Name.Attribute, 'attr'),
            (r'/?\s*>', Name.Tag, '#pop'),
        ],
        'script-content': [
            (r'<\s*/\s*script\s*>', Name.Tag, '#pop'),
            (r'.+?(?=<\s*/\s*script\s*>)', using(JavascriptLexer)),
        ],
        'style-content': [
            (r'<\s*/\s*style\s*>', Name.Tag, '#pop'),
            (r'.+?(?=<\s*/\s*style\s*>)', using(CssLexer)),
        ],
        'attr': [
            ('".*?"', String, '#pop'),
            ("'.*?'", String, '#pop'),
            (r'[^\s>]+', String, '#pop'),
        ],
    }

    def analyse_text(text):
        if html_doctype_matches(text):
            return 0.5


class PhpLexer(RegexLexer):
    name = 'PHP'
    aliases = ['php', 'php3', 'php4', 'php5']
    filenames = ['*.php', '*.php[345]']

    flags = re.IGNORECASE | re.DOTALL | re.MULTILINE
    tokens = {
        'root': [
            (r'<\?(php)?', Comment.Preproc, 'php'),
            (r'[^<]+', Other),
            (r'<', Other)
        ],
        'php': [
            (r'\?>', Comment.Preproc, '#pop'),
            (r'<<<([a-zA-Z_][a-zA-Z0-9_]*)\n.*?\n\1\;?\n', String),
            (r'\s+', Text),
            (r'#.*?\n', Comment),
            (r'//.*?\n', Comment),
            (r'/\*.*?\*/', Comment),
            (r'(->|::)(\s*)([a-zA-Z_][a-zA-Z0-9_]*)',
             bygroups(Operator, Text, Name.Attribute)),
            (r'[~!%^&*()+=|\[\]:;,.<>/?{}@-]', Text),
            (r'(class)(\s+)', bygroups(Keyword, Text), 'classname'),
            (r'(function)(\s+)', bygroups(Keyword, Text), 'functionname'),
            (r'(and|E_PARSE|old_function|E_ERROR|or|as|E_WARNING|parent|'
             r'eval|PHP_OS|break|exit|case|extends|PHP_VERSION|cfunction|'
             r'FALSE|print|for|require|continue|foreach|require_once|'
             r'declare|return|default|static|do|switch|die|stdClass|'
             r'echo|else|TRUE|elseif|var|empty|if|xor|enddeclare|include|'
             r'virtual|endfor|include_once|while|endforeach|global|__FILE__|'
             r'endif|list|__LINE__|endswitch|new|__sleep|endwhile|not|'
             r'array|__wakeup|E_ALL|NULL|final|php_user_filter|interface|'
             r'implements|public|private|protected|abstract|clone|try|'
             r'catch|throw|this)\b', Keyword),
            ('(true|false|null)\b', Keyword.Constant),
            (r'\$[a-zA-Z_][a-zA-Z0-9_]*', Name.Variable),
            ('[a-zA-Z_][a-zA-Z0-9_]*', Name.Other),
            (r"[0-9](\.[0-9]*)?(eE[+-][0-9])?[flFLdD]?|"
             r"0[xX][0-9a-fA-F]+[Ll]?", Number),
            (r'"(\\\\|\\"|[^"])*"', String.Double),
            (r"'(\\\\|\\'|[^'])*'", String.Single)
        ],
        'classname': [
            (r'[a-zA-Z_][a-zA-Z0-9_]*', Name.Class, '#pop')
        ],
        'functionname': [
            (r'[a-zA-Z_][a-zA-Z0-9_]*', Name.Function, '#pop')
        ]
    }

    def __init__(self, **options):
        self.funcnamehighlighting = get_bool_opt(
            options, 'funcnamehighlighting', True)
        self.disabledmodules = get_list_opt(
            options, 'disabledmodules', ['unknown'])
        self.startinline = get_bool_opt(options, 'startinline', False)

        # collect activated functions in a set
        self._functions = set()
        if self.funcnamehighlighting:
            from pygments.lexers._phpbuiltins import MODULES
            for key, value in MODULES.iteritems():
                if key not in self.disabledmodules:
                    self._functions.update(value)
        RegexLexer.__init__(self, **options)

    def get_tokens_unprocessed(self, text):
        stack = ['root']
        if self.startinline:
            stack.append('php')
        for index, token, value in \
            RegexLexer.get_tokens_unprocessed(self, text, stack):
            if token is Name.Other:
                if value in self._functions:
                    yield index, Name.Function, value
                    continue
            yield index, token, value

    def analyse_text(text):
        rv = 0.0
        for tag in '<?php', '?>':
            if tag in text:
                rv += 0.2
        return rv


class XmlLexer(RegexLexer):
    flags = re.MULTILINE | re.DOTALL

    name = 'XML'
    aliases = ['xml']
    filenames = ['*.xml']
    mimetypes = ['text/xml', 'application/xml', 'image/svg+xml']

    tokens = {
        'root': [
            ('[^<&]+', Text),
            ('&.*?;', Name.Entity),
            (r'\<\!\[CDATA\[.*?\]\]\>', Comment.Preproc),
            ('<!--', Comment, 'comment'),
            (r'<\?.*?\?>', Comment.Preproc),
            ('<![^>]*>', Comment.Preproc),
            (r'<\s*[a-zA-Z0-9:-]+', Name.Tag, 'tag'),
            (r'<\s*/\s*[a-zA-Z0-9:-]+\s*>', Name.Tag),
        ],
        'comment': [
            ('[^-]+', Comment),
            ('-->', Comment, '#pop'),
            ('-', Comment),
        ],
        'tag': [
            (r'\s+', Text),
            (r'[a-zA-Z0-9_:-]+\s*=', Name.Attribute, 'attr'),
            (r'/?\s*>', Name.Tag, '#pop'),
        ],
        'attr': [
            ('\s+', Text),
            ('".*?"', String, '#pop'),
            ("'.*?'", String, '#pop'),
            (r'[^\s>]+', String, '#pop'),
        ],
    }

    def analyse_text(text):
        if looks_like_xml(text):
            return 0.5
