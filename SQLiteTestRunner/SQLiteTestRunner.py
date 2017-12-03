# -*- coding: utf-8 -*-
import warnings
import sqlite3
import logging
from datetime import datetime
import unittest


logger = logging.getLogger()


initial_log_sql = """
    CREATE TABLE IF NOT EXISTS log(
        LogTime TEXT,
        LogLevel TEXT,
        Message TEXT,
        Module TEXT,
        LineNo INT,
        Exception TEXT,
        Timestamp INT
    )"""
insertion_log_sql = """
    INSERT INTO log(
        LogTime, LogLevel, Message, Module, LineNo, Exception, Timestamp
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?
    )"""


class SQLiteHandler(logging.Handler):
    def __init__(self, db=None):
        logging.Handler.__init__(self)
        self.db = db if db else 'log.db'
        self.fmt = logging.Formatter()
        conn = sqlite3.connect(self.db)
        conn.execute(initial_log_sql)
        conn.commit()

    def emit(self, record):
        self.format(record)
        if record.exc_info:
            record.exc_text = self.fmt.formatException(record.exc_info)
        else:
            record.exc_text = ''
        conn = sqlite3.connect(self.db)
        conn.execute(insertion_log_sql, (record.asctime,
                                         record.levelname,
                                         record.message,
                                         record.module,
                                         record.lineno,
                                         record.exc_text,
                                         round(record.created*1000)))
        conn.commit()


html_template = r"""<!DOCTYPE html>
<html lang="en">
<script src="https://rawgit.com/kripken/sql.js/master/js/sql.js"></script>
<script language="javascript" type="text/javascript">
    result_db = "%(reportdb)s";
    log_db = "%(logdb)s";
    // result_table
    id = 0;
    module = 1;
    case_class = 2;
    method = 3;
    desc = 4;
    result = 5;
    message = 6;
    start = 7;
    end = 8;
    // log_table
    logtime = 0;
    loglevel = 1;
    logmessage = 2;
    logmodule = 3;
    lineno = 4;
    exception = 5;
    timestamp = 6;


    function calculateDuration(start, end) {
        duration_num = new Date(end) - new Date(start);
        second_gap = 1000
        minute_gap = 60 * second_gap
        hour_gap = 60 * minute_gap
        day_gap = 24 * hour_gap
        days = Math.floor(duration_num / day_gap);
        hours = Math.floor((duration_num %% day_gap) / hour_gap);
        minutes = Math.floor((duration_num %% hour_gap) / minute_gap);
        seconds = Math.floor((duration_num %% minute_gap) / second_gap);
        micro_seconds = duration_num %% 1000;
        duration_str = '';
        if (days > 0) duration_str += days + 'd';
        if (hours > 0) duration_str += hours + 'h';
        if (minutes > 0) duration_str += minutes + 'm';
        if (seconds > 0) duration_str += seconds + 's';
        if (micro_seconds > 0) duration_str += micro_seconds + 'ms';
        if (micro_seconds == 0 && duration_str == '') duration_str = '<1ms';
        return duration_str
    }


    function loadBinaryFile(db_path, success) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", db_path, true);
        xhr.responseType = "arraybuffer";
        xhr.onload = function() {
            var data = new Uint8Array(xhr.response);
            var arr = new Array();
            for(var i = 0; i != data.length; ++i) arr[i] = String.fromCharCode(data[i]);
            success(arr.join(""));
        };
        xhr.send();
    };

    function init(){
        datatable = document.getElementById('result_table');
        showAllData();
    }

    function removeAllData(){
        for(var i = datatable.childNodes.length-1;i>=0;i--){
            datatable.removeChild(datatable.childNodes[i]);
        }
    }
    
    function getModuleResultCount(module, count, pass, failed, error, skip, tr){
        loadBinaryFile(result_db, function(data){
            var db = new SQL.Database(data);
            // Database is ready
            var sql_result = db.exec("SELECT result, COUNT(*) AS count FROM testcase " +
                                     "WHERE module='" + module + "' " + "AND class IS NOT NULL " +
                                     "AND method IS NOT NULL GROUP BY result");
            result_count = 0
            for(var i=0; i<sql_result[0].values.length; i++){
                 if (sql_result[0].values[i][0] == 'Pass') {
                    pass.innerHTML = sql_result[0].values[i][1];
                 }
                 if (sql_result[0].values[i][0] == 'Skip') {
                    skip.innerHTML = sql_result[0].values[i][1];
                 }
                 if (sql_result[0].values[i][0] == 'Failure') {
                    failed.innerHTML = sql_result[0].values[i][1];
                 }
                 if (sql_result[0].values[i][0] == 'Error') {
                    error.innerHTML = sql_result[0].values[i][1];
                 }
                 result_count += sql_result[0].values[i][1];
            }
            if (error.innerHTML !== null && error.innerHTML !== '') {
                tr.className = 'errorModule';
            } else if (failed.innerHTML !== null && failed.innerHTML !== '') {
                tr.className = 'failModule';
            } else if (skip.innerHTML !== null && skip.innerHTML !== '') {
                tr.className = 'skipModule';
            } else {
                tr.className = 'passModule';
            }
            count.innerHTML = result_count;
        });
    }

    function getClassResultCount(module, case_class, count, pass, failed, error, skip, tr){
        loadBinaryFile(result_db, function(data){
            var db = new SQL.Database(data);
            // Database is ready
            var sql_result = db.exec("SELECT result, COUNT(*) AS count FROM testcase " +
                                     "WHERE module='" + module + "' " + "AND class='" + case_class + "' " +
                                     "AND method IS NOT NULL GROUP BY result");
            result_count = 0
            for(var i=0; i<sql_result[0].values.length; i++){
                 if (sql_result[0].values[i][0] == 'Pass') {
                    pass.innerHTML = sql_result[0].values[i][1];
                 }
                 if (sql_result[0].values[i][0] == 'Skip') {
                    skip.innerHTML = sql_result[0].values[i][1];
                 }
                 if (sql_result[0].values[i][0] == 'Failure') {
                    failed.innerHTML = sql_result[0].values[i][1];
                 }
                 if (sql_result[0].values[i][0] == 'Error') {
                    error.innerHTML = sql_result[0].values[i][1];
                 }
                 result_count += sql_result[0].values[i][1];
            }
            if (error.innerHTML !== null && error.innerHTML !== '') {
                tr.className = 'errorClass';
            } else if (failed.innerHTML !== null && failed.innerHTML !== '') {
                tr.className = 'failClass';
            } else if (skip.innerHTML !== null && skip.innerHTML !== '') {
                tr.className = 'skipClass';
            } else {
                tr.className = 'passClass';
            }
            count.innerHTML = result_count;
        });
    }

    function showResult(row){
        document.getElementsByTagName('title')[0].innerHTML = row[desc];
        document.getElementById('title').innerHTML =  row[desc];
        start_time = document.getElementById('StartTime');
        start_time.innerHTML += row[start];
        end_time = document.getElementById('EndTime');
        end_time.innerHTML += row[end];
        test_duration = document.getElementById('Duration');
        test_duration.innerHTML += calculateDuration(row[start], row[end]);
        loadBinaryFile(result_db, function(data){
            var db = new SQL.Database(data);
            // Database is ready
            var sql_result = db.exec("SELECT result, COUNT(*) AS count FROM testcase " +
                                     "WHERE module IS NOT NULL AND class IS NOT NULL " +
                                     "AND method IS NOT NULL GROUP BY result");
            var status_arr = new Array()
            result_count = 0
            for(var i=0; i<sql_result[0].values.length; i++){
                status_arr.push(sql_result[0].values[i][0] + ' ' + sql_result[0].values[i][1])
                result_count += sql_result[0].values[i][1];
            }
            document.getElementById('Status').innerHTML += 'Total ' + result_count + ', ' + status_arr.join(', ');
        });
    }
    
    function showModule(row){
        var tr = document.createElement('tr');
        var mod_name = document.createElement('td');
        mod_name.innerHTML = row[module];
        var count = document.createElement('td');
        var pass = document.createElement('td');
        var failed = document.createElement('td');
        var error = document.createElement('td');
        var skip = document.createElement('td');
        getModuleResultCount(row[module], count, pass, failed, error, skip, tr)
        var duration = document.createElement('td');
        duration.innerHTML = calculateDuration(row[start], row[end]);
        var mod_modify = document.createElement('td');
        var mod_log_link = document.createElement('a')
        mod_log_link.innerHTML = 'View Log';
        mod_log_link.href = 'javascript:showLog("' + row[module] + '", null, null, "' + 
                            row[start] + '", "' + row[end] + '")';
        mod_modify.appendChild(mod_log_link);

        tr.appendChild(mod_name);
        tr.appendChild(count);
        tr.appendChild(pass);
        tr.appendChild(failed);
        tr.appendChild(error);
        tr.appendChild(skip);
        tr.appendChild(duration);
        tr.appendChild(mod_modify);

        datatable.appendChild(tr);
    }

    function showClass(row){
        var tr = document.createElement('tr');
        var cls_name = document.createElement('td');
        cls_name.innerHTML = row[module] + '.' + row[case_class];
        var count = document.createElement('td');
        var pass = document.createElement('td');
        var failed = document.createElement('td');
        var error = document.createElement('td');
        var skip = document.createElement('td');
        getClassResultCount(row[module], row[case_class], count, pass, failed, error, skip, tr)
        var duration = document.createElement('td');
        duration.innerHTML = calculateDuration(row[start], row[end]);
        var cls_modify = document.createElement('td');
        var cls_log_link = document.createElement('a')
        cls_log_link.innerHTML = 'View Log';
        cls_log_link.href = 'javascript:showLog("' + row[module] + '", "' + row[case_class] + '", null, "' + 
                            row[start] + '", "' + row[end] + '")';
        cls_modify.appendChild(cls_log_link);

        tr.appendChild(cls_name);
        tr.appendChild(count);
        tr.appendChild(pass);
        tr.appendChild(failed);
        tr.appendChild(error);
        tr.appendChild(skip);
        tr.appendChild(duration);
        tr.appendChild(cls_modify);

        datatable.appendChild(tr);
    }

    function showCase(row){
        var tr = document.createElement('tr');
        var name = document.createElement('td');
        if (row[desc] !== null) {
            name.innerHTML = row[method] + ': ' + row[desc];
        } else {
            name.innerHTML = row[method];
        }
        var case_result = document.createElement('td');
        case_result.colSpan = 5;
        case_result.align = 'center';
        var case_modify_link = document.createElement('a')
        case_modify_link.innerHTML = row[result];
        case_modify_link.href = 'javascript:showModify("' + row[module] + '", "' +
                             row[case_class] + '", "' + row[method] + '")';
        case_result.appendChild(case_modify_link);
        var duration = document.createElement('td');
        duration.innerHTML = calculateDuration(row[start], row[end]);
        var case_log_td = document.createElement('td');
        case_log_td.align = 'center';
        var case_log_link = document.createElement('a')
        case_log_link.innerHTML = 'View Log';
        case_log_link.href = 'javascript:showLog("' + row[module] + '", "' + row[case_class] + '", "'
                             + row[method] + '", "' + row[start] + '", "' + row[end] + '")';
        case_log_td.appendChild(case_log_link);

        tr.appendChild(name);
        tr.appendChild(case_result);
        tr.appendChild(duration);
        tr.appendChild(case_log_td);

        if (row[result] == 'Error') {
            tr.className = 'errorCase';
        } else if (row[result] == 'Failure') {
            tr.className = 'failCase';
        } else if (row[result] == 'Skip') {
            tr.className = 'skipCase';
        } else {
            tr.className = 'passCase';
        }

        datatable.appendChild(tr);
    }

    function showData(row){
        if (row[module] !== null) {
            if (row[case_class] === null) {
                showModule(row)
            } else {
                if (row[method] === null) {
                    showClass(row);
                } else {
                    showCase(row);
                }
            }  
        } else {
            showResult(row);
        }
    }


    function showAllData(){
        resultDiv = document.getElementById('result_div');
        resultDiv.style.height = (window.innerHeight - resultDiv.getBoundingClientRect()['y'] - 20) + 'px';
        loadBinaryFile(result_db, function(data){
            var db = new SQL.Database(data);
            // Database is ready
            var sql_result = db.exec("SELECT * FROM testcase");
            removeAllData();
            for(var i=0; i<sql_result[0].values.length; i++){
                showData(sql_result[0].values[i]);
            }
        });
    }

    function getLogStringLines(sql_result) {
        var log_arr = new Array();
        for(var i=0; i<sql_result[0].values.length; i++){
            if (sql_result[0].values[i][exception] !== null && sql_result[0].values[i][exception] !== '') {
                log_arr.push(sql_result[0].values[i][logtime] + '-[' +
                                sql_result[0].values[i][loglevel] + '][' +
                                sql_result[0].values[i][logmodule] + '] ' +
                                sql_result[0].values[i][logmessage] + ', ' +
                                sql_result[0].values[i][exception]);
            } else {
                log_arr.push(sql_result[0].values[i][logtime] + '-[' +
                                sql_result[0].values[i][loglevel] + '][' +
                                sql_result[0].values[i][logmodule] + '] ' +
                                sql_result[0].values[i][logmessage]);
            }
        }
        return log_arr;
    }

    function generateLog(start, end, gap_start, gap_end) {
        loadBinaryFile(log_db, function(data){
            var db = new SQL.Database(data);
            var sql_result = null;
            // Database is ready
            if (gap_start !== null && gap_end !== null) {
                sql_result_begin = db.exec("SELECT * FROM log WHERE Timestamp >= " + new Date(start).getTime() +
                                           " AND Timestamp < " + new Date(gap_start).getTime());
                sql_result_end = db.exec("SELECT * FROM log WHERE Timestamp > " + new Date(gap_end).getTime() +
                                         " AND Timestamp <= " + new Date(end).getTime());
                log_arr_start = getLogStringLines(sql_result_begin);
                log_arr_start.push("...\n    Test Case Running\n...");
                log_arr_end = getLogStringLines(sql_result_end)
                log_arr = log_arr_start.concat(log_arr_end);
            } else {
                sql_result = db.exec("SELECT * FROM log WHERE Timestamp >= " + new Date(start).getTime() +
                                     " AND Timestamp <= " + new Date(end).getTime());
                log_arr = getLogStringLines(sql_result);
            }
            document.getElementById('log_content').innerHTML = log_arr.join('\n');
        });
    }

    function showLog(module_str, class_str, method_str, case_start, case_stop) {
        document.getElementById('log_content').innerHTML = '';
        document.getElementById('logDiv').style.display = 'block';
        document.getElementById('case_log').style.height = (
            document.getElementById('logDiv').clientHeight
            - window.getComputedStyle(document.getElementsByClassName('divHeader')[0], null)['height'].replace('px', '')
            ) + 'px';
        loadBinaryFile(result_db, function(data){
            var db = new SQL.Database(data);
            // Database is ready
            if (class_str === null) {
                document.getElementById('log_title').innerHTML = 'Log: ' + module_str;
                var sql_result = db.exec("SELECT MIN(startTime) AS min_start, MAX(endTime) AS max_end FROM testcase " +
                                         "WHERE module='" + module_str + "' AND class IS NOT NULL");
                generateLog(case_start, case_stop, sql_result[0].values[0][0], sql_result[0].values[0][1])
            } else if (method_str === null) {
                document.getElementById('log_title').innerHTML = 'Log: ' + module_str + '.' + class_str;
                var sql_result = db.exec("SELECT MIN(startTime) AS min_start, MAX(endTime) AS max_end FROM testcase " +
                                         "WHERE module='" + module_str + "' AND class='" + class_str + "' AND method IS NOT NULL");
                generateLog(case_start, case_stop, sql_result[0].values[0][0], sql_result[0].values[0][1])
            } else {
                document.getElementById('log_title').innerHTML = 'Log: ' + module_str + '.' + class_str + '.' + method_str;
                generateLog(case_start, case_stop, null, null);
            }
        });
        showMask();
    }

    function showModify(module_str, class_str, method_str) {
        document.getElementById('modifyDiv').style.display = 'block';
        document.getElementById('modify_title').innerHTML = 'Modify: ' + module_str + '.' +
                                                            class_str + '.' + method_str;
        showMask();
    }

    function showMask() {
        document.getElementById('maskDiv').style.display = 'block';
        var maskDiv = document.getElementById('maskDiv');
        maskDiv.style.width = document.documentElement.clientWidth + 'px';
        maskDiv.style.height = document.documentElement.clientHeight + 'px';
    }

    function hideDiv() {
        document.getElementById('logDiv').style.display = 'none';
        document.getElementById('modifyDiv').style.display = 'none';
        document.getElementById('maskDiv').style.display = 'none';
    }

</script>
<head>
    <meta charset="UTF-8">
    <title>Test Report</title>
    <style type="text/css" media="screen">
        body        { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 80%%; }
        table       { font-size: 100%%; }
        pre         { margin-left: 20px; font-size: 12px; line-height: 20px; }

        /* -- heading ---------------------------------------------------------------------- */
        h1                   { font-size: 16pt; color: #34495e; }
        .heading             { margin-top: 0ex; margin-bottom: 1ex; }
        .heading.attribute   { margin-top: 1ex; margin-bottom: 0; }
        .heading.description { margin-top: 4ex; margin-bottom: 6ex; }
        pre                  { white-space: pre-wrap; word-wrap: break-word; }

        /* -- css div popup ----------------------------------------------------------------- */
        .popDiv {
            position: fixed;
            position: absolute;
            background-color: white;
            top: 10%%;
            left: 10%%;
            width: 80%%;
            height: 80%%;
            z-index: 999;
        }
        #maskDiv {
            position: absolute;
            background-color: #bebebe;
            opacity: 0.5;
            top: 0px;
            left: 0px;
        }
        #closeDiv{
            cursor: pointer; 
            position: absolute; 
            right: 0px; 
            top: 0px;
            width:60px;
            height:40px;
            border:2px black none;
            background-color:#2c3e50;
            text-align: center;
            vertical-align: middle;
            font-size: 20px;
            font-weight: bold;
            color: white;
        }
        .divHeader{
            width: 100%%;
            height: 40px;
            background-color:#2c3e50;
        }
        .divTitle{
            color: white;
            font-size: 20px;
            font-weight: bold;
            line-height: 40px;
            margin-left: 10px;
            vertical-align: middle;
        }
        /* -- report ------------------------------------------------------------------------ */
        .passModule  { background-color: #27ae60; }
        .failModule  { background-color: #f39c12; }
        .errorModule { background-color: #c0392b; }
        .skipModule  { background-color: #2980b9; }
        .passClass  { background-color: #2ecc71; }
        .failClass  { background-color: #f1c40f; }
        .errorClass { background-color: #e74c3c; }
        .skipClass  { background-color: #3498db; }
        .passCase   { color: #000; }
        .failCase   { color: #f39c12; font-weight: bold; }
        .errorCase  { color: #c0392b; font-weight: bold; }
        .skipCase   { color: #2980b9; font-weight: bold; }
        .hiddenRow  { display: none; }
        .testcase   { margin-left: 2em; }

        .table-head {
            padding-right:17px;
            background-color:#34495e;
        }
        .table-head th {
            font-weight: bold;
            font-size: 15px;
            color: white;
            padding: 0px;
            height: 30px;
            vertical-align: middle;
            text-align: left;
        }
        .table-head th:nth-child(n+2) {
            text-align: center;
        }
        .table-body {
            width:100%%; 
            overflow-y: scroll;
        }
        .table-body td {
            border: 1px solid #34495e;
            padding: 2px;
        }
        .table-body td:nth-child(n+2) {
            text-align: center;
        }
        .table-head table,.table-body table {
            width:100%%;
            border-collapse:collapse;
        }
    </style>
</head>
<body onload="javascript:init()">
    <div class='heading'>
        <h1 id="title">Test Report</h1>
        <p class='attribute' id='StartTime'><strong>Start Time: </strong></p>
        <p class='attribute' id='EndTime'><strong>End Time: </strong></p>
        <p class='attribute' id='Duration'><strong>Duration: </strong></p>
        <p class='attribute' id='Status'><strong>Status: </strong></p>
    </div>
    <div style="width: 100%%;">
        <div class="table-head">
            <table>
                <colgroup>
                    <col/>
                    <col style="width: 50px;"/>
                    <col style="width: 50px;"/>
                    <col style="width: 50px;"/>
                    <col style="width: 50px;"/>
                    <col style="width: 50px;"/>
                    <col style="width: 100px;"/>
                    <col style="width: 100px;"/>
                </colgroup>
                <thead>
                    <tr>
                        <th>Test Module/Test Class/Test Case</th>
                        <th>Count</th>
                        <th>Pass</th>
                        <th>Failed</th>
                        <th>Error</th>
                        <th>Skip</th>
                        <th>Duration</th>
                        <th>Log</th>
                    </tr>
                </thead>
            </table>
        </div>
        <div id='result_div' class="table-body">
            <table>
                <colgroup>
                    <col/>
                    <col style="width: 50px;"/>
                    <col style="width: 50px;"/>
                    <col style="width: 50px;"/>
                    <col style="width: 50px;"/>
                    <col style="width: 50px;"/>
                    <col style="width: 100px;"/>
                    <col style="width: 100px;"/>
                </colgroup>
                <tbody id="result_table">
                </tbody>
            </table>
        </div>
    </div>
</body>
<div id="maskDiv" onclick="javascript:hideDiv()" style="display: none;"></div>
<div id="logDiv" class="popDiv" style="display: none;">
    <div class="divHeader"><span id='log_title' class="divTitle"></span>
        <button id="closeDiv" onclick="javascript:hideDiv()">✖</button></div>
    <div id='case_log' style="width: 100%%; overflow-y: scroll;"><pre id='log_content'></pre></div>
</div>
<div id="modifyDiv" class="popDiv" style="display: none;">
    <div class="divHeader"><span id='modify_title' class="divTitle"></span>
        <button id="closeDiv" onclick="javascript:hideDiv()">✖</button></div>
    <pre id='case_modify'></pre>
</div>
</html>
"""


initial_case_sql = """
    CREATE TABLE IF NOT EXISTS testcase(
        id INTEGER PRIMARY KEY,
        module TEXT,
        class TEXT,
        method TEXT,
        description TEXT,
        result TEXT,
        message TEXT,
        startTime TEXT,
        endTime TEXT
    )"""
insertion_case_sql = """
    INSERT INTO testcase(module, class, method, description) VALUES (?, ?, ?, ?)"""
insertion_cls_sql = """
    INSERT INTO testcase (module, class) SELECT * FROM (SELECT ?, ?) AS tmp 
    WHERE NOT EXISTS (SELECT module, class FROM testcase WHERE module=? AND class=?) LIMIT 1;"""
insertion_mod_sql = """
    INSERT INTO testcase (module) SELECT * FROM (SELECT ?) AS tmp 
    WHERE NOT EXISTS (SELECT module FROM testcase WHERE module=?) LIMIT 1;"""
update_case_start_sql = """
    UPDATE testcase SET startTime=? WHERE module=? AND class=? AND method=? AND startTime IS NULL"""
update_case_result_sql = """
    UPDATE testcase SET result=? WHERE module=? AND class=? AND method=?"""
update_case_end_sql = """
    UPDATE testcase SET endTime=? WHERE module=? AND class=? AND method=?"""
update_case_msg_sql = """
    UPDATE testcase SET message=? WHERE module=? AND class=? AND method=?"""
update_cls_start_sql = """
    UPDATE testcase SET startTime=? WHERE module=? AND class=? AND method IS NULL AND startTime IS NULL"""
update_cls_end_sql = """
    UPDATE testcase SET endTime=? WHERE module=? AND class=? AND method IS NULL"""
update_cls_msg_sql = """
    UPDATE testcase SET message=? WHERE module=? AND class=? AND method IS NULL"""
update_mod_start_sql = """
    UPDATE testcase SET startTime=? WHERE module=? AND class IS NULL AND method IS NULL AND startTime IS NULL"""
update_mod_end_sql = """
    UPDATE testcase SET endTime=? WHERE module=? AND class IS NULL AND method IS NULL"""
update_mod_msg_sql = """
    UPDATE testcase SET message=? WHERE module=? AND class IS NULL AND method IS NULL"""
update_test_start_sql = """
    UPDATE testcase SET startTime=? WHERE module IS NULL AND class IS NULL AND method IS NULL AND startTime IS NULL"""
update_test_end_sql = """
    UPDATE testcase SET endTime=? WHERE module IS NULL AND class IS NULL AND method IS NULL"""
update_test_msg_sql = """
    UPDATE testcase SET message=? WHERE module IS NULL AND class IS NULL AND method IS NULL"""


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
            logger.info('Case [{0} {1} {2}] finished at {3}'.format(
                mod, cls, method, datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]))
            conn.execute(update_case_end_sql, (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], mod, cls, method))
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

    def addSuccess(self, test):
        self.update_case(test.__module__, test.__class__.__name__, getattr(test, '_testMethodName'),
                         result='Pass', end=True)
        super(SQLiteTestResult, self).addSuccess(test)

    def addError(self, test, err):
        self.update_case(test.__module__, test.__class__.__name__, getattr(test, '_testMethodName'),
                         result='Error', end=True, msg=self._exc_info_to_string(err, test))
        super(SQLiteTestResult, self).addError(test, err)

    def addFailure(self, test, err):
        self.update_case(test.__module__, test.__class__.__name__, getattr(test, '_testMethodName'),
                         result='Failure', end=True, msg=self._exc_info_to_string(err, test))
        super(SQLiteTestResult, self).addFailure(test, err)

    def addSkip(self, test, reason):
        self.update_case(test.__module__, test.__class__.__name__, getattr(test, '_testMethodName'),
                         result='Skip', end=True, msg=reason)
        super(SQLiteTestResult, self).addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self.update_case(test.__module__, test.__class__.__name__, getattr(test, '_testMethodName'),
                         result='Failure', end=True, msg=self._exc_info_to_string(err, test))
        super(SQLiteTestResult, self).addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self.update_case(test.__module__, test.__class__.__name__, getattr(test, '_testMethodName'),
                         result='Pass', end=True)
        super(SQLiteTestResult, self).addUnexpectedSuccess(test)


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
        logger.info('Class: {0} finished at {1}'.format(test_cls.__name__, datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
        conn.execute(update_cls_end_sql,
                     (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], test_cls.__module__, test_cls.__name__))
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
        logger.info('Module: {0} finished at {1}'.format(test_mod, datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
        conn.execute(update_mod_end_sql,
                     (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], test_mod))
    conn.commit()


def _handleClassSetUp(self, test, result):
    if getattr(result, '_previousTestClass', None) != test.__class__:
        self.update_class(result.db, test.__class__, start=datetime.now())
    super(self.__class__, self)._handleClassSetUp(test, result)


def _tearDownPreviousClass(self, test, result):
    super(self.__class__, self)._tearDownPreviousClass(test, result)
    previous_class = getattr(result, '_previousTestClass', None)
    result.currentModule = test.__class__.__module__ if test is not None else None
    if previous_class and previous_class != test.__class__:
        self.update_class(result.db, previous_class, end=True)


def _handleModuleTearDown(self, result):
    super(self.__class__, self)._handleModuleTearDown(result)
    previousModule = self._get_previous_module(result)
    if previousModule and previousModule != result.currentModule:
        self.update_module(result.db, previousModule, end=True)
    if result.currentModule and previousModule != result.currentModule:
        self.update_module(result.db, result.currentModule, start=datetime.now())


class SQLiteTestRunner(object):
    """A test runner class that saves results to a local database file, and displays results by html.
    """
    resultclass = SQLiteTestResult

    def __init__(self, db=None, html=None, descriptions=True, verbosity=1,
                 failfast=False, buffer=False, resultclass=None, warnings=None,
                 *, tb_locals=False):
        """Construct a SQLiteTestRunner.
        """
        self.db = db if db else 'result.db'
        self.html = html if html else 'report.html'
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.buffer = buffer
        self.tb_locals = tb_locals
        self.warnings = warnings
        if resultclass is not None:
            self.resultclass = resultclass

    def _makeResult(self):
        return self.resultclass(self.db, self.descriptions)

    def alter_test_suite(self, suites):
        if isinstance(suites, unittest.TestSuite) and not isinstance(suites, self.suiteClass):
            suites.__class__ = self.suiteClass
        if isinstance(suites, unittest.TestSuite) and getattr(suites, '_tests', None) is not None:
            for suite in getattr(suites, '_tests'):
                self.alter_test_suite(suite)

    def alter_suite_class(self, test):
        self.suiteClass = type(
            'SQLiteTestSuite', (test.__class__,),
            dict(_handleClassSetUp=_handleClassSetUp, _tearDownPreviousClass=_tearDownPreviousClass,
                 _handleModuleTearDown=_handleModuleTearDown,
                 update_class=update_class, update_module=update_module))
        test_suite = self.suiteClass(test)
        self.alter_test_suite(test_suite)
        return test_suite

    def add_case(self, conn, cases):
        if isinstance(cases, unittest.TestSuite) and len(getattr(cases, '_tests')) > 0:
            for case in cases:
                if isinstance(case, unittest.TestSuite):
                    self.add_case(conn, case)
                else:
                    conn.execute(insertion_mod_sql, (
                        case.__module__, case.__module__))
                    conn.execute(insertion_cls_sql, (
                        case.__module__, case.__class__.__name__,
                        case.__module__, case.__class__.__name__))
                    conn.execute(insertion_case_sql, (
                        case.__module__, case.__class__.__name__,
                        getattr(case, '_testMethodName'), case.shortDescription()))

    def init_db_case_list(self, suite):
        conn = sqlite3.connect(self.db)
        conn.execute(initial_case_sql)
        conn.execute(insertion_case_sql, (None, None, None, self.descriptions))
        self.add_case(conn, suite)
        conn.commit()

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
            # Generate html report at first
            html_tmpl_dict = dict(reportdb=self.db, logdb='')
            for handler in logger.handlers:
                if isinstance(handler, SQLiteHandler):
                    html_tmpl_dict['logdb'] = handler.db
            with open(self.html, 'w', encoding='utf-8') as report_html:
                report_html.write(html_template % html_tmpl_dict)
            test_suite = self.alter_suite_class(test)
            self.init_db_case_list(test_suite)
            self.update_report(start=datetime.now())
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
        return result
