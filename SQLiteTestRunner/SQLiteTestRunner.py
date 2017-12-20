# -*- coding: utf-8 -*-
import os
import sys
import warnings
import sqlite3
import logging
from datetime import datetime
import unittest
import jinja2

logger = logging.getLogger()


test_log_gap_tips = """
...
    Test Case Running...
...

"""


initial_case_sql = """
    CREATE TABLE IF NOT EXISTS testcase(
        module TEXT,
        class TEXT,
        method TEXT,
        origin TEXT,
        description TEXT,
        result TEXT,
        message TEXT,
        startTime TEXT,
        endTime TEXT,
        logs TEXT
    )"""
# Add and update info of a test case
insertion_case_sql = """
    INSERT INTO testcase (module, class, method, origin, description, logs) VALUES (?, ?, ?, ?, ?, '')"""
update_case_origin_sql = """
    UPDATE testcase SET message=? WHERE module=? AND class=? AND method=?"""
update_case_start_sql = """
    UPDATE testcase SET startTime=? WHERE module=? AND class=? AND method=? AND startTime IS NULL"""
update_case_result_sql = """
    UPDATE testcase SET result=? WHERE module=? AND class=? AND method=?"""
update_case_end_sql = """
    UPDATE testcase SET endTime=? WHERE module=? AND class=? AND method=?"""
update_case_msg_sql = """
    UPDATE testcase SET message=? WHERE module=? AND class=? AND method=?"""
update_case_log_sql = """
    UPDATE testcase SET logs=logs||? WHERE module=? AND class=? AND method=?"""
# Add and update info of a test class
insertion_cls_sql = """
    INSERT INTO testcase (module, class, description, logs) SELECT * FROM (SELECT ?, ?, ?, '') AS tmp 
    WHERE NOT EXISTS (SELECT module, class FROM testcase WHERE module=? AND class=?) LIMIT 1;"""
update_cls_start_sql = """
    UPDATE testcase SET startTime=? WHERE module=? AND class=? AND method IS NULL AND startTime IS NULL"""
update_cls_end_sql = """
    UPDATE testcase SET endTime=? WHERE module=? AND class=? AND method IS NULL"""
update_cls_msg_sql = """
    UPDATE testcase SET message=? WHERE module=? AND class=? AND method IS NULL"""
update_cls_log_sql = """
    UPDATE testcase SET logs=logs||? WHERE module=? AND class=? AND method IS NULL"""
# Add and update info of a test module
insertion_mod_sql = """
    INSERT INTO testcase (module, description, logs) SELECT * FROM (SELECT ?, ?, '') AS tmp 
    WHERE NOT EXISTS (SELECT module FROM testcase WHERE module=?) LIMIT 1;"""
update_mod_start_sql = """
    UPDATE testcase SET startTime=? WHERE module=? AND class IS NULL AND method IS NULL AND startTime IS NULL"""
update_mod_end_sql = """
    UPDATE testcase SET endTime=? WHERE module=? AND class IS NULL AND method IS NULL"""
update_mod_msg_sql = """
    UPDATE testcase SET message=? WHERE module=? AND class IS NULL AND method IS NULL"""
update_mod_log_sql = """
    UPDATE testcase SET logs=logs||? WHERE module=? AND class IS NULL AND method IS NULL"""
# Add and update info of whole test
insertion_test_sql = """
    INSERT INTO testcase (description, logs) SELECT * FROM (SELECT ?, '') AS tmp 
    WHERE NOT EXISTS (SELECT module FROM testcase WHERE module IS NULL) LIMIT 1;"""
update_test_start_sql = """
    UPDATE testcase SET startTime=? WHERE module IS NULL AND class IS NULL AND method IS NULL AND startTime IS NULL"""
update_test_end_sql = """
    UPDATE testcase SET endTime=? WHERE module IS NULL AND class IS NULL AND method IS NULL"""
update_test_msg_sql = """
    UPDATE testcase SET message=? WHERE module IS NULL AND class IS NULL AND method IS NULL"""
update_test_log_sql = """
    UPDATE testcase SET logs=logs||? WHERE module IS NULL AND class IS NULL AND method IS NULL"""
# Get test case to rerun
select_rerun_module = """
    SELECT DISTINCT module FROM testcase WHERE method IS NOT NULL AND 
    (result IS NULL OR result IN ({0}))"""
select_rerun_class = """
    SELECT DISTINCT module, class FROM testcase WHERE method IS NOT NULL AND 
    (result IS NULL OR result IN ({0}))"""
select_rerun_method = """
    SELECT DISTINCT module, class, origin FROM testcase WHERE method IS NOT NULL AND origin IS NOT NULL AND 
    (result IS NULL OR result IN ({0}))"""
select_origin_method = """
    SELECT DISTINCT origin FROM testcase WHERE module=? AND class=? AND method=? AND origin IS NOT NULL"""
select_parameterized_method = """
    SELECT DISTINCT method FROM testcase WHERE module=? AND class=? AND origin=? AND method IS NOT NULL"""
update_test_case_method = """
    UPDATE testcase SET result=NULL, startTime=NULL WHERE module=? AND class=? AND method=?"""
update_parameterized_method = """
    UPDATE testcase SET method=?, description=?, result=NULL, startTime=NULL 
    WHERE module=? AND class=? AND method=? AND origin=?"""


class TestHandler(logging.Handler):
    """A handler to capture logs during test case execution.

    Used by SQLiteTestRunner.
    """

    @classmethod
    def get_handler(cls):
        if len(logger.handlers) == 0:
            logger.level = logging.INFO
        for handler in logger.handlers:
            if isinstance(handler, cls):
                return handler
        else:
            handler = cls()
            logger.addHandler(handler)
            return handler

    def __init__(self):
        logging.Handler.__init__(self)
        self.logs_cache = ''

    def emit(self, record):
        msg = self.format(record)
        msg = msg if msg[-1] == '\n' else msg + '\n'
        self.logs_cache += msg
    
    def store_cache(self, db, sql, args, gap_tips=False):
        conn = sqlite3.connect(db)
        if gap_tips:
            conn.execute(sql, tuple([test_log_gap_tips] + list(args)))
        conn.execute(sql, tuple([self.logs_cache] + list(args)))
        conn.commit()
        self.logs_cache = ''


class SQLiteTestResult(unittest.TestResult):
    """A test result class that can save results to a local database file.

    Used by SQLiteTestRunner.
    """

    def __init__(self, db=None, descriptions=None):
        super(SQLiteTestResult, self).__init__(None, descriptions, None)
        self.db = db if db else 'result.db'
        self.descriptions = descriptions

    def update_case(self, mod, cls, method, start=None, end=None, result=None, msg=None):
        conn = sqlite3.connect(self.db)
        if start:
            conn.execute(update_case_start_sql, (start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], mod, cls, method))
            logger.info('Case [{0} {1} {2}] start at {3}'.format(
                mod, cls, method, start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]))
        if result:
            logger.info('Case [{0} {1} {2}] is {3}'.format(mod, cls, method, result))
            conn.execute(update_case_result_sql, (result, mod, cls, method))
        if msg:
            logger.info('Case [{0} {1} {2}] output: {3}'.format(mod, cls, method, msg))
            conn.execute(update_case_msg_sql, (msg, mod, cls, method))
        if end:
            conn.execute(update_case_end_sql, (end.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], mod, cls, method))
            logger.info('Case [{0} {1} {2}] finished at {3}'.format(
                mod, cls, method, end.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]))
        conn.commit()

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return '\n'.join((str(test), doc_first_line))
        else:
            return str(test)

    def startTest(self, test):
        self.update_case(test.__module__, test.__class__.__name__, getattr(test, '_testMethodName'),
                         start=datetime.now())
        super(SQLiteTestResult, self).startTest(test)
    
    def stopTest(self, test):
        super(SQLiteTestResult, self).stopTest(test)
        TestHandler.get_handler().store_cache(
            self.db, update_case_log_sql, (test.__module__, test.__class__.__name__, getattr(test, '_testMethodName')))

    def addSuccess(self, test):
        self.update_case(test.__module__, test.__class__.__name__, getattr(test, '_testMethodName'),
                         result='PASS', end=datetime.now())
        super(SQLiteTestResult, self).addSuccess(test)

    def addError(self, test, err):
        self.update_case(test.__module__, test.__class__.__name__, getattr(test, '_testMethodName'),
                         result='ERROR', end=datetime.now(), msg=self._exc_info_to_string(err, test))
        super(SQLiteTestResult, self).addError(test, err)

    def addFailure(self, test, err):
        self.update_case(test.__module__, test.__class__.__name__, getattr(test, '_testMethodName'),
                         result='FAIL', end=datetime.now(), msg=self._exc_info_to_string(err, test))
        super(SQLiteTestResult, self).addFailure(test, err)

    def addSkip(self, test, reason):
        self.update_case(test.__module__, test.__class__.__name__, getattr(test, '_testMethodName'),
                         result='SKIP', end=datetime.now(), msg=reason)
        super(SQLiteTestResult, self).addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self.update_case(test.__module__, test.__class__.__name__, getattr(test, '_testMethodName'),
                         result='FAIL', end=datetime.now(), msg=self._exc_info_to_string(err, test))
        super(SQLiteTestResult, self).addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self.update_case(test.__module__, test.__class__.__name__, getattr(test, '_testMethodName'),
                         result='PASS', end=datetime.now())
        super(SQLiteTestResult, self).addUnexpectedSuccess(test)


isnotsuite = getattr(unittest.suite, '_isnotsuite')


class SQLiteTestSuite(unittest.TestSuite):

    @classmethod
    def update_class(cls, db, test_cls, start=None, end=None, message=None):
        conn = sqlite3.connect(db)
        if start:
            conn.execute(update_cls_start_sql,
                         (start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], test_cls.__module__, test_cls.__name__))
            logger.info('Class: {0} start at {1}'.format(test_cls.__name__, start.strftime('%Y-%m-%d %H:%M:%S.%f')))
        if message:
            conn.execute(update_cls_msg_sql, (message, test_cls.__module__, test_cls.__name__))
            logger.info('Class: {0} output: {1}'.format(test_cls.__name__, message))
        if end:
            conn.execute(update_cls_end_sql,
                         (end.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], test_cls.__module__, test_cls.__name__))
            logger.info('Class: {0} finished at {1}'.format(test_cls.__name__, end.strftime('%Y-%m-%d %H:%M:%S.%f')))
        conn.commit()

    @classmethod
    def update_module(cls, db, test_mod, start=None, end=None, message=None):
        conn = sqlite3.connect(db)
        if start:
            conn.execute(update_mod_start_sql,
                         (start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], test_mod))
            logger.info('Module: {0} start at {1}'.format(test_mod, start.strftime('%Y-%m-%d %H:%M:%S.%f')))
        if message:
            conn.execute(update_mod_msg_sql, (message, test_mod))
            logger.info('Module: {0} output: {1}'.format(test_mod, message))
        if end:
            logger.info('Module: {0} finished at {1}'.format(test_mod, end.strftime('%Y-%m-%d %H:%M:%S.%f')))
            conn.execute(update_mod_end_sql,
                         (end.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], test_mod))
        conn.commit()

    def _handleClassSetUp(self, test, result):
        if getattr(result, '_previousTestClass', None) != test.__class__:
            self.update_class(result.db, test.__class__, start=datetime.now())
        super(self.__class__, self)._handleClassSetUp(test, result)
        if getattr(result, '_previousTestClass', None) != test.__class__:
            TestHandler.get_handler().store_cache(
                self.db, update_cls_log_sql, (test.__class__.__module__, test.__class__.__name__))

    def _tearDownPreviousClass(self, test, result):
        super(self.__class__, self)._tearDownPreviousClass(test, result)
        previous_class = getattr(result, '_previousTestClass', None)
        result.currentModule = test.__class__.__module__ if test is not None else None
        if previous_class and previous_class != test.__class__:
            self.update_class(result.db, previous_class, end=datetime.now())
            TestHandler.get_handler().store_cache(
                self.db, update_cls_log_sql, (previous_class.__module__, previous_class.__name__), gap_tips=True)

    def _handleModuleFixture(self, test, result):
        previousModule = self._get_previous_module(result)
        super(self.__class__, self)._handleModuleFixture(test, result)
        if test.__class__.__module__ and previousModule != test.__class__.__module__:
            TestHandler.get_handler().store_cache(self.db, update_mod_log_sql, (test.__class__.__module__,))

    def _handleModuleTearDown(self, result):
        super(self.__class__, self)._handleModuleTearDown(result)
        previousModule = self._get_previous_module(result)
        if previousModule and previousModule != result.currentModule:
            self.update_module(result.db, previousModule, end=datetime.now())
            TestHandler.get_handler().store_cache(self.db, update_mod_log_sql, (previousModule,), gap_tips=True)
        if result.currentModule and previousModule != result.currentModule:
            self.update_module(result.db, result.currentModule, start=datetime.now())

    @classmethod
    def alter_super_class(cls, suite_cls):
        if suite_cls.__mro__[0] is not SQLiteTestSuite:
            setattr(SQLiteTestSuite, '__bases__', suite_cls.__mro__)

    def alter_suite_class(self):
        for test in self._tests:
            if not isnotsuite(test):
                test.__class__ = self.__class__
                test.db = self.db
                test.alter_suite_class()


class SQLiteTestRunner(object):
    """A test runner class that saves results to a local database file, and displays results by html.
    """
    resultclass = SQLiteTestResult

    def __init__(self, db=None, html=None, descriptions=True, verbosity=1, 
                 rerun=False, rerun_status=None, rerun_level='class',
                 failfast=False, buffer=False, resultclass=None, warnings=None,
                 *, tb_locals=False):
        """Construct a SQLiteTestRunner.
        """
        self.db = db if db else 'result.db'
        self.html = html if html else 'report.html'
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.rerun = rerun
        self.rerun_status = tuple([status.upper() for status in rerun_status]) if rerun_status else tuple()
        self.rerun_level = rerun_level
        self.buffer = buffer
        self.tb_locals = tb_locals
        self.warnings = warnings
        if resultclass is not None:
            self.resultclass = resultclass

    def _makeResult(self):
        return self.resultclass(self.db, self.descriptions)

    def alter_suite_class(self, test):
        SQLiteTestSuite.alter_super_class(test.__class__)
        test.__class__ = SQLiteTestSuite
        test.db = self.db
        test.alter_suite_class()
        return test

    def add_case(self, conn, cases):
        if not isnotsuite(cases) and len(getattr(cases, '_tests')) > 0:
            for case in cases:
                if isnotsuite(case):
                    conn.execute(insertion_mod_sql, (
                        case.__module__, sys.modules[case.__module__].__doc__, case.__module__))
                    conn.execute(insertion_cls_sql, (
                        case.__module__, case.__class__.__name__, case.__class__.__doc__,
                        case.__module__, case.__class__.__name__))
                    conn.execute(insertion_case_sql, (
                        case.__module__, case.__class__.__name__, getattr(case, '_testMethodName'),
                        self.get_origin_method_from_case(case), case.shortDescription()))
                else:
                    self.add_case(conn, case)

    def init_db_case_list(self, suite):
        conn = sqlite3.connect(self.db)
        conn.execute(initial_case_sql)
        conn.execute(insertion_test_sql, (self.descriptions,))
        self.add_case(conn, suite)
        conn.commit()

    def get_origin_method_from_db(self, test_module, test_class, test_method):
        conn = sqlite3.connect(self.db)
        origin_method = conn.execute(select_origin_method, (test_module, test_class, test_method)).fetchall()
        conn.commit()
        if origin_method and origin_method[0][0]:
            return origin_method[0][0]
        else:
            return None

    @classmethod
    def get_origin_method_from_case(cls, test_case):
        test_method = getattr(test_case.__class__, getattr(test_case, '_testMethodName'))
        if test_method.__closure__:
            return test_method.__closure__[0].cell_contents.__name__
        else:
            return test_method.__name__

    @classmethod
    def is_parameterized_case(self, test_case):
        test_method = getattr(test_case.__class__, getattr(test_case, '_testMethodName'))
        return test_method.__closure__ is not None and test_method.__closure__[
                                                           0].cell_contents.__name__ != test_method.__name__

    def prepare_db_for_rerun(self, conn, test_suite):
        if isinstance(test_suite, unittest.TestSuite) and len(getattr(test_suite, '_tests')) > 0:
            rerun_parameterized_case = dict()
            for case in test_suite:
                if isinstance(case, unittest.TestSuite):
                    self.prepare_db_for_rerun(conn, case)
                else:
                    if self.is_parameterized_case(case):
                        case_dict_key = '-'.join(
                            [case.__module__, case.__class__.__name__, self.get_origin_method_from_case(case)])
                        if rerun_parameterized_case.get(case_dict_key) is None:
                            rerun_parameterized_case[case_dict_key] = list()
                        rerun_parameterized_case[case_dict_key].append(case)
                    else:
                        conn.execute(update_test_case_method,
                                     (case.__module__, case.__class__.__name__, getattr(case, '_testMethodName')))
            for method, cases in rerun_parameterized_case.items():
                db_cases = conn.execute(select_parameterized_method, tuple(method.split('-'))).fetchall()
                for db_case, case in list(zip(db_cases, cases)):
                    conn.execute(update_parameterized_method,
                                 (getattr(case, '_testMethodName'), case.shortDescription(), method.split('-')[0],
                                  method.split('-')[1], db_case[0], self.get_origin_method_from_case(case)))

    def get_rerun_case(self, test_suite):
        conn = sqlite3.connect(self.db)
        rerun_test_suite = test_suite.__class__()
        if self.rerun_level == 'module':
            rerun_test_list = conn.execute(
                select_rerun_module.format(','.join(['?'] * len(self.rerun_status))),
                self.rerun_status).fetchall()
            conn.commit()
            for test_module in rerun_test_list:
                rerun_test_suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(
                    sys.modules[test_module[0]]))
        elif self.rerun_level == 'class':
            rerun_test_list = conn.execute(
                select_rerun_class.format(','.join(['?'] * len(self.rerun_status))),
                self.rerun_status).fetchall()
            conn.commit()
            for test_module, test_class in rerun_test_list:
                rerun_test_suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(
                    getattr(sys.modules[test_module], test_class)))
        elif self.rerun_level == 'method':
            class_list = conn.execute(
                select_rerun_class.format(','.join(['?'] * len(self.rerun_status))),
                self.rerun_status).fetchall()
            rerun_test_list = conn.execute(
                select_rerun_method.format(','.join(['?'] * len(self.rerun_status))), self.rerun_status).fetchall()
            conn.commit()
            # Get case from test class
            for test_module, test_class in class_list:
                test_class_cases = unittest.defaultTestLoader.loadTestsFromTestCase(
                    getattr(sys.modules[test_module], test_class))
                # Remove case that not need to be rerun
                remove_case = []
                for case in test_class_cases:
                    if (test_module, test_class, self.get_origin_method_from_case(case)) not in rerun_test_list:
                        remove_case.append(case)
                for case in remove_case:
                    getattr(test_class_cases, '_tests').remove(case)
                rerun_test_suite.addTests(test_class_cases)
        else:
            raise ValueError('No such rerun level, must be module, class or method')
        conn = sqlite3.connect(self.db)
        self.prepare_db_for_rerun(conn, rerun_test_suite)
        conn.commit()
        rerun_test_suite.db = self.db
        rerun_test_suite.alter_suite_class()
        return rerun_test_suite

    def update_report(self, start=None, end=None):
        conn = sqlite3.connect(self.db)
        if start:
            conn.execute(update_test_start_sql, (start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],))
            logger.info('Test {0} start at {1}'.format(
                self.descriptions, start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]))
        if end:
            conn.execute(update_test_end_sql, (end.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],))
            logger.info('Test {0} finished at {1}'.format(
                self.descriptions, end.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]))
        conn.commit()

    def run(self, test):
        """Run the given test case or test suite."""
        TestHandler.get_handler()
        result = self._makeResult()
        unittest.signals.registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        result.tb_locals = self.tb_locals
        with warnings.catch_warnings():
            if self.warnings:
                warnings.simplefilter(self.warnings)
                if self.warnings in ['default', 'always']:
                    warnings.filterwarnings('module',
                                            category=DeprecationWarning,
                                            message='Please use assert\w+ instead.')
            test_suite = self.alter_suite_class(test)
            if self.rerun:
                test_suite = self.get_rerun_case(test_suite)
            else:
                # Generate html report at first
                html_tmpl_dict = dict(reportdb=self.db)
                template_loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(__file__))
                template_env = jinja2.Environment(loader=template_loader)
                report_template = template_env.get_template('report_template.html')
                with open(self.html, 'w', encoding='utf-8') as report_html:
                    report_html.write(report_template.render(**html_tmpl_dict))
                self.init_db_case_list(test_suite)
                self.update_report(start=datetime.now())
            TestHandler.get_handler().store_cache(self.db, update_test_log_sql, tuple())
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()
            try:
                test_suite(result)
            finally:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()
            self.update_report(end=datetime.now())
        TestHandler.get_handler().store_cache(self.db, update_test_log_sql, tuple(), gap_tips=True)
        return result
