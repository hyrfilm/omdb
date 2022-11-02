#!/usr/bin/env python
import sys
import logging
import unittest
import argparse
import fnmatch

logging.getLogger().setLevel(logging.WARN)


def filter_suite(suite, test_pattern):
    def match_tests(suite_or_tests, pattern):
        matched = []
        for suite_or_test in suite_or_tests:
            if hasattr(suite_or_test, "_tests"):
                matched.extend(match_tests(suite_or_test._tests, pattern))
            else:
                if fnmatch.fnmatch(suite_or_test._testMethodName, pattern):
                    matched.append(suite_or_test)
        return matched

    filtered_suite = unittest.TestSuite()
    filtered_suite.addTests(match_tests(suite, test_pattern))
    return filtered_suite


def test(pattern, test_pattern):
    print("======================================================================")
    print("Running tests")
    print("======================================================================")

    suite = unittest.TestLoader().discover('backend/test', pattern=pattern)

    if test_pattern:
        suite = filter_suite(suite, test_pattern)
    result = unittest.TextTestRunner(stream=sys.stdout).run(suite)

    return len(result.failures) + len(result.errors)


def test_coverage(pattern, test_pattern, coverage):
    if coverage:
        try:
            from coverage import coverage

            cov = coverage(
                include=["backend/*"],
                omit=["backend/test/*"])

            cov.start()
        except ImportError:
            print("coverage not installed, can't collect coverage data")
            coverage = False

    failures = test(pattern, test_pattern)

    if coverage:
        cov.stop()

        print("======================================================================")
        print("Coverage report")
        print("======================================================================")

        if hasattr(cov, 'set_option'):
            cov.set_option("report:show_missing", True)

            cov.report()

    return failures


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--coverage", dest="coverage", action="store_true", default=False,
                        help="Collect and output coverage data")
    parser.add_argument("-p", "--pattern", dest="pattern", default="test_*.py",
                        help="Run test files matching given pattern")
    parser.add_argument("-t", "--test-pattern", dest="test_pattern",
                        help="Run test methods matching given pattern")

    args = parser.parse_args()

    failures = test_coverage(args.pattern, args.test_pattern, args.coverage)

    print("======================================================================")
    print("Done!")

    exit(failures != 0)
