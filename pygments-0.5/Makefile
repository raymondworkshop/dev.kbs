#
# Makefile for Pygments
# ~~~~~~~~~~~~~~~~~~~~~
#
# Combines scripts for common tasks.
#
# :copyright: 2006 by Georg Brandl.
# :license: GNU GPL, see LICENSE for more details.
#

PYTHON ?= python

export PYTHONPATH = $(shell python -c 'print ":".join(line.strip() for line in file("PYTHONPATH"))' 2>/dev/null)

.PHONY: apidocs check clean clean-pyc codetags docs epydoc lexermap \
	pylint reindent test

apidocs: epydoc

check:
	@$(PYTHON) scripts/check_sources.py -i apidocs -i pygments/lexers/_mapping.py \
		   -i docs/build

clean: clean-pyc
	rm -f codetags.html
	rm -rf apidocs

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

codetags:
	@$(PYTHON) scripts/find_codetags.py -i apidocs -i scripts/pylintrc \
		   -i scripts/find_codetags.py -o codetags.html .

docs: docs/build

docs/build: docs/src/*.txt
	$(PYTHON) docs/generate.py html docs/build $?
	touch docs/build

epydoc:
	@rm -rf apidocs
	@$(PYTHON) -Wi:default_transform `which epydoc` -o apidocs --css scripts/epydoc.css \
		   --url http://trac.pocoo.org/pygments --no-frames --docformat restructuredtext \
		   -v pygments
	@sed -i -e 's|^<br />||' \
			-e 's|\s\+$$||' \
			-e 's|^\s\+</pre>|</pre>|' \
			-e 's|\(<table class="[^"]*"\) border="1"|\1|' \
			-e 's|\(<table class="navbar" .*\) width="100%"|\1|' \
			-e 's|<td width="15%"|<td class="spacer"|' \
			apidocs/*.html
	@$(PYTHON) scripts/fix_epydoc_markup.py apidocs

lexermap:
	cd pygments/lexers; $(PYTHON) _mapping.py

pylint:
	@pylint --rcfile scripts/pylintrc pygments

reindent:
	@$(PYTHON) scripts/reindent.py -r -B .

test:
	@$(PYTHON) tests/run.py $(TESTS)
