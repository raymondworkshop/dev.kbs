# -*- coding: utf-8 -*-
"""
    Pygments unit tests
    ~~~~~~~~~~~~~~~~~~

    Usage::

        python run.py [testfile ...]


    :copyright: 2006 by Georg Brandl.
    :license: GNU GPL, see LICENSE for more details.
"""

import sys, os, new
import unittest
import __builtin__

from os.path import dirname, basename, join, abspath

testdir = abspath(dirname(__file__))

# useful for all tests
__builtin__.testdir = testdir

failed = []
total_test_count = 0
error_test_count = 0


def err(file, what, exc):
    print >>sys.stderr, file, 'failed %s:' % what,
    print >>sys.stderr, exc
    failed.append(file[:-3])


class QuietTestRunner(object):
    """Customized test runner for relatively quiet output"""

    def __init__(self, testname, stream=sys.stderr):
        self.testname = testname
        self.stream = unittest._WritelnDecorator(stream)

    def run(self, test):
        global total_test_count
        global error_test_count
        result = unittest._TextTestResult(self.stream, True, 1)
        test(result)
        if not result.wasSuccessful():
            self.stream.write(' FAIL:')
            result.printErrors()
            failed.append(self.testname)
        else:
            self.stream.write(' ok\n')
        total_test_count += result.testsRun
        error_test_count += len(result.errors) + len(result.failures)
        return result


def run_tests():
    # needed to avoid confusion involving atexit handlers
    import logging

    orig_modules = sys.modules.keys()

    if sys.argv[1:]:
        # test only files given on cmdline
        files = [entry + '.py' for entry in sys.argv[1:] if entry.startswith('test_')]
    else:
        files = [entry for entry in os.listdir(testdir)
                 if (entry.startswith('test_') and entry.endswith('.py'))]
        files.sort()

    print >>sys.stderr, '    Pygments Test Suite running, stand by...    '
    print >>sys.stderr, '==============================================='

    for testfile in files:
        globs = {}
        try:
            execfile(join(testdir, testfile), globs)
        except Exception, exc:
            raise
            err(testfile, 'execfile', exc)
            continue
        sys.stderr.write(testfile[:-3] + ': ')
        try:
            runner = QuietTestRunner(testfile[:-3])
            # make a test suite of all TestCases in the file
            tests = []
            for name, thing in globs.iteritems():
                if name.endswith('Test'):
                    tests.append((name, unittest.makeSuite(thing)))
            # PY24: use key keyword arg
            tests.sort(lambda x, y: cmp(x[0], y[0]))
            suite = unittest.TestSuite()
            suite.addTests([x[1] for x in tests])
            runner.run(suite)
        except Exception, exc:
            err(testfile, 'running test', exc)

    print >>sys.stderr, '==============================================='
    if failed:
        print >>sys.stderr, '%d of %d tests failed.' % \
              (error_test_count, total_test_count)
        print >>sys.stderr, 'Tests failed in:', ', '.join(failed)
        return 1
    else:
        if total_test_count == 1:
            print >>sys.stderr, '1 test happy.'
        else:
            print >>sys.stderr, 'All %d tests happy.' % total_test_count
        return 0


if __name__ == '__main__':
    sys.exit(run_tests())
