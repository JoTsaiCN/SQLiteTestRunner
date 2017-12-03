# -*- coding: utf-8 -*-
from unittest import TestCase
import logging

logger = logging.getLogger()


def setUpModule():
    logger.debug('Set up module')


def tearDownModule():
    logger.debug('Tear down module')


class TestStringMethods(TestCase):
    """ Example test. """

    def test_upper(self):
        self.assertEqual('upper'.upper(), 'UPPER')

    def test_isupper(self):
        self.assertTrue('UPPER'.isupper())
        self.assertFalse('upper'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def test_fail(self):
        """ This test should fail. """
        self.assertEqual(0, 1)

    def test_skip(self):
        """ This test should be skipped. """
        self.skipTest("This is a skipped test.")


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
