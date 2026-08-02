import io
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from typing import NamedTuple
from unittest import TestCase, TestLoader, TextTestRunner, TestSuite
from unittest.runner import TextTestResult, _WritelnDecorator
import argparse

# Enhanced timing information
# https://hackernoon.com/timing-tests-in-python-for-fun-and-profit-1663144571


class TimeLoggingTestResult(TextTestResult):

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_timings = []
        self.stream = stream
        self.showAll = verbosity > 1

    def startTest(self, test):
        self._test_started_at = time.time()
        super().startTest(test)

    def addSuccess(self, test):
        elapsed = time.time() - self._test_started_at
        name = self.getDescription(test)
        self.test_timings.append((name, elapsed))

        if self.showAll:
            self.stream.write("({:.03}s)  ".format(round(elapsed, 3)))

        super().addSuccess(test)

    def getTestTimings(self):
        return self.test_timings


def print_slow_tests(stream, timings, slow_test_threshold):
    """Write a 'Slow Tests' report for any (name, elapsed) pair in
    'timings' that exceeds 'slow_test_threshold' seconds."""
    if slow_test_threshold is None:
        return

    results = [(name, elapsed) for name, elapsed in timings
               if elapsed > slow_test_threshold]

    if len(results) > 0:
        s = "\nSlow Tests (>{:.03}s):".format(slow_test_threshold)
        stream.writeln(s)

        results.sort(key=lambda x: x[1])

        for name, elapsed in results:
            stream.writeln(
                "({:.03}s) {}".format(
                    elapsed, name))


class TimeLoggingTestRunner(TextTestRunner):

    def __init__(self, slow_test_threshold=None, *args, **kwargs):
        self.slow_test_threshold = slow_test_threshold
        return super().__init__(
            resultclass=TimeLoggingTestResult,
            *args,
            **kwargs,
        )

    def run(self, test):
        result = super().run(test)
        print_slow_tests(self.stream, result.getTestTimings(),
                         self.slow_test_threshold)
        return result


def iterate_tests(test_suite_or_case):
    """Iterate through all of the test cases in 'test_suite_or_case'.
    https://stackoverflow.com/questions/15487587/
    python-unittest-get-testcase-ids-from-nested-testsuite
    """
    try:
        suite = iter(test_suite_or_case)
    except TypeError:
        yield test_suite_or_case
    else:
        for test in suite:
            for subtest in iterate_tests(test):
                yield subtest


def round_robin_chunks(tests, n):
    """Split 'tests' into up to 'n' round-robin chunks, skipping any
    that end up empty (e.g. when n exceeds len(tests))."""
    chunks = [tests[i::n] for i in range(n)]
    return [chunk for chunk in chunks if chunk]


class ChunkResult(NamedTuple):
    text: str
    timings: list
    tests_run: int
    failures: int
    errors: int
    skipped: int


def run_test_chunk(tests, verbosity):
    """Run 'tests' (a list of TestCase instances) in a single worker
    process, capturing output to a buffer instead of stdout. This is a
    module-level function so it can be pickled for ProcessPoolExecutor."""
    suite = TestSuite(tests)
    stream = io.StringIO()
    runner = TimeLoggingTestRunner(slow_test_threshold=None,
                                   stream=stream, verbosity=verbosity)
    result = runner.run(suite)

    return ChunkResult(
        text=stream.getvalue(),
        timings=result.getTestTimings(),
        tests_run=result.testsRun,
        failures=len(result.failures),
        errors=len(result.errors),
        skipped=len(result.skipped),
    )


if __name__ == '__main__':
    # Get command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbosity",
                        type=int, default=1, choices=[0, 1, 2],
                        help="verbosity of test output; default is 1")

    parser.add_argument("-p", "--pattern",
                        default="*.py",
                        help="pattern of modules to test; default is *.py",)

    parser.add_argument('-d', '--directory',
                        help='root directory of the tests')

    parser.add_argument('-l', '--longtests', action='store_true',
                        help='run long running tests; default is false')

    parser.add_argument('-t', '--threshold',
                        type=float, default=5.0,
                        help=('threshold in seconds for considering a test '
                              'long running'))

    parser.add_argument('-j', '--parallel', action='store_true',
                        help=('run tests in parallel using multiple '
                              'processes; default is false'))

    default_threads = max(1, (os.cpu_count() or 3) - 2)
    parser.add_argument('-n', '--threads',
                        type=int, default=default_threads,
                        help=('number of worker processes to use with '
                              '--parallel; default is system core count '
                              'minus 2 (currently {})'.format(default_threads)))

    args = parser.parse_args()

    # Get list of test cases to run
    test_loader = TestLoader()
    test_suite_discovered = test_loader.discover(args.directory,
                                                 pattern=args.pattern)

    # Flatten into individual test cases, stripping out long running
    # tests, if necessary
    flat_tests = [test for test in iterate_tests(test_suite_discovered)
                  if args.longtests
                  or not test._testMethodName.startswith('test_long_')]

    sth = None if args.longtests else args.threshold

    if args.parallel:
        chunks = round_robin_chunks(flat_tests, args.threads)

        with ProcessPoolExecutor(max_workers=args.threads) as executor:
            futures = [executor.submit(run_test_chunk, chunk, args.verbosity)
                       for chunk in chunks]

            all_timings = []
            total_run = total_failures = total_errors = total_skipped = 0
            for future in futures:
                chunk_result = future.result()
                print(chunk_result.text, end='')

                all_timings.extend(chunk_result.timings)
                total_run += chunk_result.tests_run
                total_failures += chunk_result.failures
                total_errors += chunk_result.errors
                total_skipped += chunk_result.skipped

        stream = _WritelnDecorator(sys.stdout)
        print_slow_tests(stream, all_timings, sth)

        print("\nRan {} tests across {} chunk(s): {} failures, "
              "{} errors, {} skipped".format(
                  total_run, len(chunks), total_failures,
                  total_errors, total_skipped))

    else:
        test_suite = TestSuite(flat_tests)
        test_runner = TimeLoggingTestRunner(slow_test_threshold=sth,
                                            verbosity=args.verbosity)

        test_runner.run(test_suite)
