# -*- coding: utf-8 -*-
import sys
import warnings
import sqlite3
import logging
from datetime import datetime
import unittest


logger = logging.getLogger()


html_template = r"""<!DOCTYPE html>
<html lang="en">
<script src="https://rawgit.com/kripken/sql.js/master/js/sql-memory-growth.js"></script>
<script language="javascript" type="text/javascript">
    result_db = "%(reportdb)s";
    // result_table
    module = 0;
    case_class = 1;
    method = 2;
    method = 3;
    desc = 4;
    result = 5;
    message = 6;
    start = 7;
    end = 8;
    logs = 9;

    function calculateDuration(start, end) {
        if(start === null) {
            return 'Not Execute';
        }
        if(end === null) {
            return 'Interruption';
        }
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

    function showStatusCase(case_result) {
        case_list = document.getElementsByClassName(case_result.toLowerCase() + 'Case');
        for(var i=0; i<case_list.length; i++) {
            case_list[i].style.display = "";
        }
        if(case_list.length > 0) {
            button = document.getElementById(case_result.toLowerCase() + 'Button');
            button.className = case_result.toLowerCase() + 'Button';
            if(document.getElementsByClassName('disableButton').length == 1) {
                document.getElementById('allButton').className = 'allButton';
            }
        }
    }

    function hideStatusCase(case_result) {
        case_list = document.getElementsByClassName(case_result + 'Case');
        for(var i=0; i<case_list.length; i++) {
            case_list[i].style.display = 'none';
        }
        if(case_list.length > 0) {
            button = document.getElementById(case_result.toLowerCase() + 'Button');
            button.className = 'disableButton';
            document.getElementById('allButton').className = 'disableButton';
        }
    }

    function changeCaseDisplay(case_result) {
        if(case_result.toLowerCase() == 'all'){
            button = document.getElementById('allButton');
            if(button.className == 'disableButton') {
                showStatusCase('error');
                showStatusCase('fail');
                showStatusCase('skip');
                showStatusCase('pass');
            } else {
                hideStatusCase('error');
                hideStatusCase('fail');
                hideStatusCase('skip');
                hideStatusCase('pass');
            }
        } else {
            if(document.getElementById(case_result.toLowerCase() + 'Button').className == 'disableButton') {
                showStatusCase(case_result.toLowerCase());
            } else {
                hideStatusCase(case_result.toLowerCase());
            }
        }
    }
    
    function getModuleResultCount(module, count, pass, failed, error, skip, tr){
        loadBinaryFile(result_db, function(data){
            var db = new SQL.Database(data);
            // Database is ready
            var sql_result = db.exec("SELECT result, COUNT(*) AS count FROM testcase " +
                                     "WHERE module='" + module + "' " + "AND class IS NOT NULL " +
                                     "AND method IS NOT NULL GROUP BY result");
            result_count = 0;
            error_count = 0;
            for(var i=0; i<sql_result[0].values.length; i++){
                 if (sql_result[0].values[i][0] == 'PASS') {
                    pass.innerHTML = sql_result[0].values[i][1];
                 }
                 if (sql_result[0].values[i][0] == 'SKIP') {
                    skip.innerHTML = sql_result[0].values[i][1];
                 }
                 if (sql_result[0].values[i][0] == 'FAIL') {
                    failed.innerHTML = sql_result[0].values[i][1];
                 }
                 if (sql_result[0].values[i][0] == 'ERROR' || sql_result[0].values[i][0] === null) {
                    error.innerHTML += sql_result[0].values[i][1];
                 }
                 result_count += sql_result[0].values[i][1];
            }
            if (error_count > 0) {
                error.innerHTML = error_count;
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
            result_count = 0;
            error_count = 0;
            for(var i=0; i<sql_result[0].values.length; i++){
                 if (sql_result[0].values[i][0] == 'PASS') {
                    pass.innerHTML = sql_result[0].values[i][1];
                 }
                 if (sql_result[0].values[i][0] == 'SKIP') {
                    skip.innerHTML = sql_result[0].values[i][1];
                 }
                 if (sql_result[0].values[i][0] == 'FAIL') {
                    failed.innerHTML = sql_result[0].values[i][1];
                 }
                 if (sql_result[0].values[i][0] == 'ERROR' || sql_result[0].values[i][0] == 'ERROR') {
                    error_count += sql_result[0].values[i][1];
                 }
                 result_count += sql_result[0].values[i][1];
            }
            if (error_count > 0) {
                error.innerHTML = error_count;
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
        document.title = row[desc];
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
            var status_arr = new Array();
            result_count = 0;
            error_count = 0;
            for(var i=0; i<sql_result[0].values.length; i++){
                if (sql_result[0].values[i][0] == 'ERROR' || sql_result[0].values[i][0] === null) {
                    error_count += sql_result[0].values[i][1];
                } else {
                    status_arr.push(sql_result[0].values[i][0] + ' ' + sql_result[0].values[i][1]);
                }
                result_count += sql_result[0].values[i][1];
            }
            if(error_count > 0) {
                status_arr.push('ERROR ' + error_count);
            }
            button = document.createElement('input');
            button.type = 'button';
            button.id = 'allButton';
            button.className = 'allButton';
            button.value = 'Total ' + result_count;
            button.onclick = Function("changeCaseDisplay('All');");
            document.getElementById('Status').appendChild(button);
            for(var i=0; i<status_arr.length; i++) {
                button = document.createElement('input');
                button.id = status_arr[i].split(' ')[0].toLowerCase() + 'Button';
                button.className = status_arr[i].split(' ')[0].toLowerCase() + 'Button';
                button.type = 'button';
                button.value = status_arr[i];
                button.onclick = Function("changeCaseDisplay('" + status_arr[i].split(' ')[0] + "');");
                document.getElementById('Status').appendChild(button);
            }
            hideStatusCase('pass');
            hideStatusCase('skip');
        });
    }
    
    function showModule(row){
        var tr = document.createElement('tr');
        var mod_name = document.createElement('td');
        if (row[desc] !== null) {
            mod_name.innerHTML = row[module] + ': ' + row[desc];
        } else {
            mod_name.innerHTML = row[module];
        }
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
        mod_log_link.href = 'javascript:showLog("' + row[module] + '", null, null)';
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
        if (row[desc] !== null) {
            cls_name.innerHTML = row[module] + '.' + row[case_class] + ': ' + row[desc];
        } else {
            cls_name.innerHTML = row[module] + '.' + row[case_class];
        }
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
        cls_log_link.href = 'javascript:showLog("' + row[module] + '", "' + row[case_class] + '", null)';
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
        name.style.paddingLeft = '10px';
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
                             + row[method] + '")';
        case_log_td.appendChild(case_log_link);

        tr.appendChild(name);
        tr.appendChild(case_result);
        tr.appendChild(duration);
        tr.appendChild(case_log_td);

        if (row[result] == 'ERROR') {
            tr.className = 'errorCase';
        } else if (row[result] == 'FAIL') {
            tr.className = 'failCase';
        } else if (row[result] == 'SKIP') {
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

    function showLog(module_str, class_str, method_str) {
        document.getElementById('log_content').innerHTML = '';
        document.getElementById('logDiv').style.display = 'block';
        document.getElementById('case_log').style.height = (
            document.getElementById('logDiv').clientHeight
            - window.getComputedStyle(document.getElementsByClassName('divHeader')[0], null)['height'].replace('px', '')
            ) + 'px';
        loadBinaryFile(result_db, function(data){
            var db = new SQL.Database(data);
            // Database is ready
            if (module_str === null) {
                document.getElementById('log_title').innerHTML = 'Log: ' + document.title;
                sql_result = db.exec("SELECT logs FROM testcase WHERE module IS NULL AND class IS NULL AND method IS NULL");
            } else if (class_str === null) {
                document.getElementById('log_title').innerHTML = 'Log: ' + module_str;
                sql_result = db.exec("SELECT logs FROM testcase " +
                                         "WHERE module='" + module_str + "' AND class IS NULL AND method IS NULL");
            } else if (method_str === null) {
                document.getElementById('log_title').innerHTML = 'Log: ' + module_str + '.' + class_str;
                sql_result = db.exec("SELECT logs FROM testcase " +
                                     "WHERE module='" + module_str + "' AND class='" + class_str + 
                                     "' AND method IS NULL");
            } else {
                document.getElementById('log_title').innerHTML = 'Log: ' + module_str + '.' + class_str + '.' + method_str;
                sql_result = db.exec("SELECT logs FROM testcase " +
                                     "WHERE module='" + module_str + "' AND class='" + class_str + 
                                     "' AND method='" + method_str + "'");
            }
            document.getElementById('log_content').innerHTML = sql_result[0].values[0][0];
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
        body        { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }
        table       { table-layout:fixed; }
        pre         { margin-left: 20px; line-height: 200%%; white-space: pre-wrap; word-wrap: break-word; }
        input       { font-size: 100%%; }

        /* -- heading ---------------------------------------------------------------------- */
        h1                   { font-size: 150%%; color: #34495e; }
        .heading             { margin-top: 0ex; margin-bottom: 1ex; }
        .heading.attribute   { margin-top: 1ex; margin-bottom: 0; }
        .heading.description { margin-top: 4ex; margin-bottom: 6ex; }

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
            font-size: 120%%;
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
            font-size: 120%%;
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

        .errorButton { background-color: #c0392b; border: 1px solid; color: white;}
        .failButton { background-color: #f39c12; border: 1px solid; color: white; }
        .skipButton { background-color: #2980b9; border: 1px solid; color: white; }
        .passButton {background-color: #27ae60; border: 1px solid; color: white; }
        .allButton { background-color: #34495e; border: 1px solid; color: white; }
        .disableButton { background-color: #eaeded; border: 1px solid; color: #34495e; border-color: white }
        
        #reportLog { color: white; }
        .table-head {
            padding-right:17px;
            background-color:#34495e;
        }
        .table-head th {
            font-weight: bold;
            color: white;
            padding: 2px;
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
            border: 1px solid #eaeded;
            padding: 2px;
            word-break:keep-all;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis;
            font-size: 90%%;
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
                        <th>PASS</th>
                        <th>FAIL</th>
                        <th>ERROR</th>
                        <th>SKIP</th>
                        <th>Duration</th>
                        <th><a id="reportLog" href="javascript:showLog(null, null, null)">Log</a></th>
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
                    sys.modules[test_module]))
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
                with open(self.html, 'w', encoding='utf-8') as report_html:
                    report_html.write(html_template % html_tmpl_dict)
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
