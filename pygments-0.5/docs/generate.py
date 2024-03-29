#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Generate Pygments Documentation
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Generates a bunch of html files containing the documentation.

    :copyright: 2006 by Armin Ronacher, Georg Brandl.
    :license: GNU LGPL, see LICENSE for more details.
"""

import os
import sys
from datetime import datetime
from cgi import escape

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.core import publish_parts
from docutils.writers import html4css1

from jinja import Template, Context, StringLoader

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


PYGMENTS_FORMATTER = HtmlFormatter(style='pastie', cssclass='syntax')

USAGE = '''\
Usage: %s <mode> <destination> [<source.txt> ...]

Generate either python or html files out of the documentation.

Mode can either be python or html.\
''' % sys.argv[0]

TEMPLATE = '''\
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
  <title>{{ title }} &mdash; Pygments</title>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <style type="text/css">
    {{ style }}
  </style>
</head>
<body>
  <div id="content">
    <h1 class="heading">Pygments</h1>
    <h2 class="subheading">{{ title }}</h2>
    {% if not file_id equals "index" %}
      <a id="backlink" href="index.html">&laquo; Back To Index</a>
    {% endif %}
    {% if toc %}
      <div class="toc">
        <h2>Contents</h2>
        <ul class="contents">
        {% for item in toc %}
          <li><a href="{{ item.0 }}">{{ item.1 }}</a></li>
        {% endfor %}
        </ul>
      </div>
    {% endif %}
    {{ body }}
  </div>
</body>
<!-- generated on: {{ generation_date }}
     file id: {{ file_id }} -->
</html>\
'''

STYLESHEET = '''\
body {
    background-color: #f2f2f2;
    margin: 0;
    padding: 0;
    font-family: 'Georgia', serif;
    color: #111;
}

#content {
    background-color: white;
    padding: 20px;
    margin: 20px auto 20px auto;
    max-width: 800px;
    border: 4px solid #ddd;
}

h1 {
    font-weight: normal;
    font-size: 40px;
    color: #09839A;
}

h2 {
    font-weight: normal;
    font-size: 30px;
    color: #C73F00;
}

h1.heading {
    margin: 0 0 30px 0;
}

h2.subheading {
    margin: -30px 0 0 45px;
}

h3 {
    margin-top: 30px;
}

table.docutils {
    border-collapse: collapse;
    border: 2px solid #aaa;
    margin: 0.5em 1.5em 0.5em 1.5em;
}

table.docutils td {
    padding: 2px;
    border: 1px solid #ddd;
}

p, li, dd, dt, blockquote {
    font-size: 15px;
    color: #333;
}

p {
    line-height: 150%;
    margin-bottom: 0;
    margin-top: 10px;
}

hr {
    border-top: 1px solid #ccc;
    border-bottom: 0;
    border-right: 0;
    border-left: 0;
    margin-bottom: 10px;
    margin-top: 20px;
}

dl {
    margin-left: 10px;
}

li, dt {
    margin-top: 5px;
}

dt {
    font-weight: bold;
}

th {
    text-align: left;
}

a {
    color: #990000;
}

a:hover {
    color: #c73f00;
}

pre {
    background-color: #f9f9f9;
    border-top: 1px solid #ccc;
    border-bottom: 1px solid #ccc;
    padding: 5px;
    font-size: 13px;
    font-family: Bitstream Vera Sans Mono,monospace;
}

tt {
    font-size: 13px;
    font-family: Bitstream Vera Sans Mono,monospace;
    color: black;
    padding: 1px 2px 1px 2px;
    background-color: #f0f0f0;
}

cite {
    /* abusing <cite>, it's generated by ReST for `x` */
    font-size: 13px;
    font-family: Bitstream Vera Sans Mono,monospace;
    font-weight: bold;
    font-style: normal;
}

#backlink {
    float: right;
    font-size: 11px;
    color: #888;
}

div.toc {
    margin: 0 0 10px 0;
}

div.toc h2 {
    font-size: 20px;
}
'''


def generate_documentation(data, link_style):
    writer = DocumentationWriter(link_style)
    parts = publish_parts(
        data,
        writer=writer,
        settings_overrides={
            'initial_header_level': 3,
            'field_name_limit': 50,
        }
    )
    return {
        'title':        parts['title'].encode('utf-8'),
        'body':         parts['body'].encode('utf-8'),
        'toc':          parts['toc']
    }


def pygments_directive(name, arguments, options, content, lineno,
                      content_offset, block_text, state, state_machine):
    try:
        lexer = get_lexer_by_name(arguments[0])
    except ValueError:
        # no lexer found
        lexer = get_lexer_by_name('text')
    parsed = highlight(u'\n'.join(content), lexer, PYGMENTS_FORMATTER)
    return [nodes.raw('', parsed, format="html")]
pygments_directive.arguments = (1, 0, 1)
pygments_directive.content = 1
directives.register_directive('sourcecode', pygments_directive)


class DocumentationWriter(html4css1.Writer):

    def __init__(self, link_style):
        html4css1.Writer.__init__(self)
        self.translator_class = create_translator(link_style)

    def translate(self):
        html4css1.Writer.translate(self)
        # generate table of contents
        contents = self.build_contents(self.document)
        contents_doc = self.document.copy()
        contents_doc.children = contents
        contents_visitor = self.translator_class(contents_doc)
        contents_doc.walkabout(contents_visitor)
        self.parts['toc'] = self._generated_toc

    def build_contents(self, node, level=0):
        sections = []
        i = len(node) - 1
        while i >= 0 and isinstance(node[i], nodes.section):
            sections.append(node[i])
            i -= 1
        sections.reverse()
        toc = []
        for section in sections:
            try:
                reference = nodes.reference('', '', refid=section['ids'][0], *section[0])
            except IndexError:
                continue
            ref_id = reference['refid']
            text = escape(reference.astext().encode('utf-8'))
            toc.append((ref_id, text))

        self._generated_toc = [('#%s' % href, caption) for href, caption in toc]
        # no further processing
        return []


def create_translator(link_style):
    class Translator(html4css1.HTMLTranslator):
        def visit_reference(self, node):
            refuri = node.get('refuri')
            if refuri is not None and '/' not in refuri and refuri.endswith('.txt'):
                node['refuri'] = link_style(refuri[:-4])
            html4css1.HTMLTranslator.visit_reference(self, node)
    return Translator


def handle_python(filename, fp, dst):
    now = datetime.now()
    title = os.path.basename(filename)[:-4]
    content = fp.read()
    def urlize(href):
        # create links for the pygments webpage
        if href == 'index.txt':
            return '/docs/'
        else:
            return '/docs/%s/' % href
    parts = generate_documentation(content, urlize)
    result = file(os.path.join(dst, title + '.py'), 'w')
    result.write('# -*- coding: utf-8 -*-\n')
    result.write('"""\n    Pygments Documentation - %s\n' % title)
    result.write('    %s\n\n' % ('~' * (24 + len(title))))
    result.write('    Generated on: %s\n"""\n\n' % now)
    result.write('import datetime\n')
    result.write('DATE = %r\n' % now)
    result.write('TITLE = %r\n' % parts['title'])
    result.write('TOC = %r\n' % parts['toc'])
    result.write('BODY = %r\n' % parts['body'])
    result.close()


def handle_html(filename, fp, dst):
    now = datetime.now()
    title = os.path.basename(filename)[:-4]
    content = fp.read()
    parts = generate_documentation(content, (lambda x: './%s.html' % x))
    result = file(os.path.join(dst, title + '.html'), 'w')
    c = Context(parts)
    c['style'] = STYLESHEET + PYGMENTS_FORMATTER.get_style_defs('.syntax')
    c['generation_date'] = now
    c['file_id'] = title
    t = Template(TEMPLATE, StringLoader())
    result.write(t.render(c).encode('utf-8'))
    result.close()


def run(handle_file, dst, sources=()):
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
    if not sources:
        sources = [os.path.join(path, fn) for fn in os.listdir(path)]
    for fn in sources:
        if not os.path.isfile(fn):
            continue
        print 'Processing %s' % fn
        f = open(fn)
        try:
            handle_file(fn, f, dst)
        finally:
            f.close()


def main(mode, dst='build/', *sources):
    try:
        handler = {
            'html':         handle_html,
            'python':       handle_python
        }[mode]
    except KeyError:
        print 'Error: unknown mode "%s"' % mode
        sys.exit(1)
    run(handler, os.path.realpath(dst), sources)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print USAGE
    else:
        main(*sys.argv[1:])
