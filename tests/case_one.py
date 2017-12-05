# -*- coding: utf-8 -*-
""" Example test module one. """
import logging
import unittest
from unittest import TestCase

from SQLiteTestRunner import SQLiteTestRunner

logger = logging.getLogger()


def setUpModule():
    logger.debug('Set up module')


def tearDownModule():
    logger.debug('Tear down module')


class TestStringMethods(TestCase):
    """ Example test one. """

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        with self.assertRaises(TypeError):
            s.split(2)

    def test_error(self):
        """ This test should be marked as error one. """
        raise ValueError

    def test_fail(self):
        """ This test should fail. """
        self.assertEqual(1, 2)

    def test_skip(self):
        """ This test should be skipped. """
        self.skipTest("This is a skipped test.")

    def test_log(self):
        for i in range(100):
            logger.debug("test log, %d" % i)


class TestStringMethodsTwo(TestCase):
    """ Example test. """

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main(testRunner=SQLiteTestRunner(
        db='test_result.db', html='test_report.html', descriptions='Test Report'))
