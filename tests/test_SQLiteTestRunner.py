# -*- coding: utf-8 -*-
import os
import unittest
import logging
from logging import config

from SQLiteTestRunner import SQLiteTestRunner


if __name__ == '__main__':
    logging.config.fileConfig('./logging_config.ini', defaults={'logfilepath': 'test.log', 'logdbpath': 'test_log.db'})
    suite = unittest.defaultTestLoader.discover(os.path.dirname(__file__), pattern='case_*.py')
    runner = SQLiteTestRunner(db='test_result.db', html='test_report.html', descriptions='Test Report')
    runner.run(suite)