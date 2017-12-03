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
