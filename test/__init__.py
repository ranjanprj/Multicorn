import doctest
import unittest

import werkzeug

def find_all_modules(packages):
    for package in packages:
        yield package
        try:
            for module in werkzeug.find_modules(package, include_packages=True,
                                                recursive=True):
                yield module
        except ValueError, e:
            if e.args != ("'%s' is not a package" % package,):
                raise

def get_tests(packages):
    """
    Return a TestSuite
    """
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for module_name in find_all_modules(packages):
        suite.addTests(loader.loadTestsFromName(module_name))
        try:
            tests = doctest.DocTestSuite(module_name)
        except ValueError, e:
            # doctest.DocTestSuite throws ValueError when there is no test
            if len(e.args) != 2 or e.args[1] != "has no tests":
                raise
        else:
            suite.addTests(tests)
    return suite

def find_TODOs(packages):
    for module_name in find_all_modules(packages):
        filename = werkzeug.import_string(module_name).__file__
        if filename[-4:] in ('.pyc', '.pyo'):
            filename = filename[:-1]
        f = open(filename)
        todo_lines = []
        todo_count = 0
        for line_no, line in enumerate(f):
            # Write 'TO' 'DO' to prevent this script from finding itself
            count = line.count('TO' 'DO')
            if count:
                todo_count += count
                todo_lines.append(line_no)
        f.close()
        if todo_count:
            yield filename, todo_count, todo_lines

def run_tests(packages):
    unittest.TextTestRunner().run(get_tests(packages))

def run_tests_with_coverage(packages):
    import coverage
    try:
        # Coverage v3 API
        c = coverage.coverage()
    except coverage.CoverageException:
        # Coverage v2 API
        c = coverage

    c.exclude('raise NotImplementedError')
    c.exclude('except ImportError:')
    c.start()
    run_tests(packages)
    c.stop()
    c.report([werkzeug.import_string(name).__file__ 
              for name in find_all_modules(p for p in packages if p != 'test')])


