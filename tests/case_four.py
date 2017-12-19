# -*- coding: utf-8 -*-
""" Example test module four. """
from unittest import TestCase
import logging
from parameterized import parameterized

logger = logging.getLogger()


def setUpModule():
    logger.debug('Set up module')


def tearDownModule():
    logger.debug('Tear down module')


class TestStringMethods(TestCase):
    """ Example test four. """

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    @parameterized.expand(input=[('hello world2', ['hello', 'world2']),
                                 ('for test1', ['for', 'test1'])])
    def test_split(self, s, sp):
        self.assertEqual(s.split(), sp)
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
