var Search = require('ace/search').Search;
var Range = require("ace/range").Range;

function search_ui (toggle) {
  if (toggle == 'replace') {
    $("#replace_term").removeAttr("disabled");
  }
  
  if (toggle == 'search') {
    $("#replace_term").attr("disabled", "disabled");
  }
  
  if (toggle == 'sin_current' || toggle == 'sin_all') {
    $("#dirchooser").css("display", "none");
  }
  
  if (toggle == 'sin_current') {
    $("#search_select, #search_wrap, #search_back").removeAttr("disabled");
  }
  
  if (toggle == 'sin_all' || toggle == 'sin_dir') {
    $("#search_select, #search_wrap, #search_back").attr("disabled", "disabled");
  }
  
  if (toggle == 'sin_dir') {
    $("#dirchooser").css("display", "block");
  }
  
  if (toggle == 'prev_next') {
    $("#next_prev").css("display", "block");
  }
  
  if (toggle == 'replace_next') {
    $("#replace_next").css("display", "block");
  }
  
  if (toggle == 'replace_all_tabs') {
    $("#replace_all_tabs").css("display", "block");
  }
  
  if (toggle == 'replace_next' || toggle == 'prev_next' || toggle == 'replace_all_tabs' || toggle == 'search_status') {
    $("#search_submit").css("display", "none");
    $("input[type='text'], input[type='checkbox'], input[type='radio']").attr('disabled', 'disabled');
  }
  
  if (toggle == 'dir_replace') {
    $("#search_status").css("display", "none");
    $("#search_status span").html('');
    
    $("#replace_status").css("display", "block");
    
    $("#replace_status_started").css("display", "none");
    $("#replace_status_started span").html('');
  }
  
  if (toggle == 'dir_replace_started') {
    $("#replace_status").css("display", "none");
    $("#replace_status_started").css("display", "block");
  }
  
  if (toggle == 'new_search') {
    $("#next_prev").css("display", "none");
    $("#replace_next").css("display", "none");
    $("#replace_all_tabs").css("display", "none");
    $("#search_status").css("display", "none");
    $("#search_status span").html('');
    
    $("#replace_status").css("display", "none");
    $("#replace_status_started").css("display", "none");
    $("#replace_status_started span").html('');
    
    $("#search_submit").css("display", "block");
    $("input[type='text'], input[type='checkbox'], input[type='radio']").removeAttr('disabled');
    
    var stype = $("input[name='stype']:checked").val();
    search_ui(stype);
    
    dirSearchJob = null;
    dirSearchTask = null;
    searchWorker = null;
    
    $("input[name='sin']:checked").click();
  }
  
  if (toggle == 'search_status' || toggle == 'replace_status') {
    $("#search_status").css("display", "block");
    
    if (toggle == 'search_status') {
      $("#search_status span").html('Searching ...');
    }
    
    else {
      $("#search_status span").html('Replacing ...');
    }
  }
}

var current_search;
var current_replace;
var current_range;
var current_backwards;
var search_options;
var searchWorker = null;
var dirSearchJob = null;
var dirSearchTask = null;

function do_search () {
  var needle = $("#search_term").val();
  var sin = $("input[name='sin']:checked").val();
  var stype = $("input[name='stype']:checked").val();
  
  current_replace = $("#replace_term").val();
  
  if (needle == '' && sin != 'dir') {
    alert('If I search for nothing I may find the end of a black hole and kill us all.');
  }
  
  else {
    search_options = {
      wrap: false,
      back: false,
      sensitive: false,
      whole: false,
      regex: false
    }
    
    for (var key in search_options) {
      if (document.getElementById('search_' + key).checked) {
        search_options[key] = true;
      }
    }
    
    search_options['needle'] = needle;
    
    if (sin == 'current') {
      current_search = false;
      if (stype == 'replace') {
        search_ui('replace_next');
      }
      
      else {
        search_ui('prev_next');
      }
      
      current_range = false;
      current_backwards = search_options['back'];
      
      search_next('forward');
    }
    
    else if (sin == 'all') {
      var opts = {
        needle: search_options['needle'],
        backwards: false,
        wrap: true,
        caseSensitive: search_options['sensitive'],
        wholeWord: search_options['whole'],
        scope: Search.ALL,
        regExp: search_options['regex']
      }
      
      current_search = new Search().set(opts);
      
      var html = '<div class="title"><em>All Tabs</em><strong>Search For: ' + search_options['needle'] + '</strong></div>';
      html += '<table>';
      html += '<tr><td><strong>Filename</strong></td><td><strong>Matches</strong></td></tr>';
      
      var item = $("#search_panel_replace");
      search_panel.select(item);
      search_panel.expand(item);
      
      for (dp in tab_paths) {
        var ranges = current_search.findAll(tab_paths[dp].session);
        if (ranges.length > 0) {
          var fn = dp.replace(basedir + "/", "");
          
          lines = '<div class="lines" id="line_results_' + tab_paths[dp].uid + '" style="display: none;">';
          for (var i=0; i < ranges.length; i++) {
            var row = ranges[i].start.row + 1;
            var col = ranges[i].start.column + 1;
            lines += '<a href="javascript: void(0)" onclick="go_to_line(\'' + escape(dp) + '\', ' + ranges[i].start.row + ', ' + ranges[i].start.column + ', ' + ranges[i].end.row + ', ' + ranges[i].end.column + ')">Line ' + row + ', Column ' + col + '</a>';
          }
          
          lines += '</div>';
          html += '<tr>';
          html += '<td><a class="expand" href="javascript: void(0)" onclick="show_line_results(\'' + tab_paths[dp].uid + '\')">' + fn +'</a>' + lines + '</td><td>' + ranges.length + '</td>';
          html += '</tr>';
        }
      }
      
      html += '</table>';
      $("#search_panel_results").html(html);
      
      size_search();
      current_range = false;
      
      if (stype == 'replace') {
        search_ui('replace_all_tabs');
      }
    }
    
    else if (sin == 'dir') {
      var glob = document.getElementById('file_glob').value;
      dir_results_started = false;
      dir_results_list = [];
      
      if (stype == 'search' && needle == '' && glob == '') {
        alert('If I search for nothing I may find the end of a black hole and kill us all.');
      }
      
      else if (stype == 'replace' && needle == '') {
        alert('If I search for nothing I may find the end of a black hole and kill us all.');
      }
      
      else {
        search_ui('search_status');
        
        var dpath = basedir + '/' + $("#picked_dir").val();
        
        $.ajax({
           type: "POST",
           dataType: 'json',
           url: "/dir_search/",
           data: {
             dir: dpath,
             'glob': glob,
             'needle': needle,
             caseSensitive: search_options['sensitive'],
             wholeWord: search_options['whole'],
             regExp: search_options['regex'],
             'replace': current_replace,
           },
           success: function (data, textStatus, jqXHR) {
             searchWorker = setTimeout(function () { check_search_status(data.task_id, data.dsid) }, 500);
           },
           error: function (jqXHR, textStatus, errorThrown) {
             alert('Error submitting search.');
             search_ui('new_search');
           }
        });
      }
    }
  }
  
  return false;
}

function check_search_status (task_id, dsid) {
  dirSearchJob = dsid;
  dirSearchTask = task_id;
  
  $.ajax({
     type: "POST",
     dataType: 'json',
     url: "/check_search/",
     data: {
       ds: dsid,
       task: task_id
     },
     success: function (data, textStatus, jqXHR) {
       set_results_dir_search(task_id, dsid, data.results);
       var stype = $("input[name='stype']:checked").val();
       
       if (data.state == 'complete') {
         if (stype == 'replace') {
           search_ui('dir_replace');
         }
         
         else {
           search_ui('new_search');
         }
       }
       
       else {
         searchWorker = setTimeout(function () { check_search_status(task_id, dsid) }, 3000);
       }
     },
     error: function (jqXHR, textStatus, errorThrown) {
       searchWorker = setTimeout(function () { check_search_status(task_id, dsid) }, 3000);
     }
  });
}

function check_replace_status (task_id, dsid) {
  dirSearchJob = dsid;
  dirSearchTask = task_id;
  
  $.ajax({
     type: "POST",
     dataType: 'json',
     url: "/check_replace/",
     data: {
       ds: dsid,
       task: task_id
     },
     success: function (data, textStatus, jqXHR) {
       if (data.state == 'complete') {
         alert('Replace Completed');
         search_ui('new_search');
       }
       
       else {
         $("#replace_status_started span").html('Working On: ' + data.last_file.replace(basedir + "/", ""));
         searchWorker = setTimeout(function () { check_replace_status(task_id, dsid) }, 3000);
       }
     },
     error: function (jqXHR, textStatus, errorThrown) {
       searchWorker = setTimeout(function () { check_replace_status(task_id, dsid) }, 3000);
     }
  });
}

var dir_results_started = false;
var dir_results_list = [];
function set_results_dir_search(task_id, dsid, results) {
  if (dir_results_started) {
    var html = '';
    for (j in results) {
      var result = results[j];
      var dp = result[0];
      var uid = result[1];
      var ranges = result[2];
      var fn = result[0].replace(basedir + "/", "");
      
      html += search_lines(dp, fn, uid, ranges);
    }
    
    $("#search_panel_results > table > tbody").append(html);
  }
  
  else {
    dir_results_started = true;
    
    var html = '<div class="title"><em>Directory</em><strong>Search For: ' + search_options['needle'] + '</strong></div>';
    html += '<table>';
    html += '<tr><td><strong>Filename</strong></td><td><strong>Matches</strong></td></tr>';
    
    var item = $("#search_panel_replace");
    search_panel.select(item);
    search_panel.expand(item);
    
    for (j in results) {
      var result = results[j];
      var dp = result[0];
      var uid = result[1];
      var ranges = result[2];
      var fn = result[0].replace(basedir + "/", "");
      
      html += search_lines(dp, fn, uid, ranges);
    }
    
    html += '</table>';
    $("#search_panel_results").html(html);
  }
  
  size_search();
}

function search_lines (dp, fn, uid, ranges) {
  var html = '';
  var dpnoa = dp.replace("'", "\\'");
  
  if (dp in dir_results_list) {}
  else {
    dir_results_list.push(dp);
    
    if (ranges.length == 0) {
      html += '<tr>';
      html += '<td><a class="expand" href="javascript: void(0)" onclick="get_file (\'' + dpnoa + '\', new Range(0, 0, 0, 0))">' + fn +'</a></td><td></td>';
      html += '</tr>';
    }
    
    else {
      var lines = '<div class="lines" id="line_results_' + uid + '" style="display: none;">';
      for (var i=0; i < ranges.length; i++) {
        var row = ranges[i][0] + 1;
        var col = ranges[i][1] + 1;
        lines += '<a href="javascript: void(0)" onclick="go_to_line(\'' + escape(dp) + '\', ' + ranges[i][0] + ', ' + ranges[i][1] + ', ' + ranges[i][0] + ', ' + ranges[i][2] + ')">Line ' + row + ', Column ' + col + '</a>';
      }
      
      lines += '</div>';
      
      html += '<tr>';
      html += '<td><a class="expand" href="javascript: void(0)" onclick="show_line_results(\'' + uid + '\')">' + fn +'</a>' + lines + '</td><td>' + ranges.length + '</td>';
      html += '</tr>';
    }
  }
  
  return html
}

function cancel_search () {
  if (searchWorker) {
    clearTimeout(searchWorker);
    $.ajax({
       type: "POST",
       dataType: 'json',
       url: "/cancel_job/",
       data: {ds: dirSearchJob, task: dirSearchTask, jtype: 'search'},
       success: function (data, textStatus, jqXHR) {
         if (data.result) {
           alert('Job Killed Successfully!');
         }
         
         else {
           alert('Job Finished Normally!');
         }
         
         search_ui('new_search');
       },
       error: function (jqXHR, textStatus, errorThrown) { alert('Error cancelling job'); }
    });
  }
}

function cancel_replace () {
  if (searchWorker) {
    clearTimeout(searchWorker);
    $.ajax({
       type: "POST",
       dataType: 'json',
       url: "/cancel_job/",
       data: {ds: dirSearchJob, task: dirSearchTask, jtype: 'replace'},
       success: function (data, textStatus, jqXHR) {
         alert('Job Killed Successfully!');
         search_ui('new_search');
       },
       error: function (jqXHR, textStatus, errorThrown) { alert('Error cancelling job'); }
    });
  }
}

function replace_dfiles () {
  search_ui('dir_replace_started');
  $("#replace_status_started span").html('Replacing ... ');
  $.ajax({
     type: "POST",
     dataType: 'json',
     url: "/dir_replace/",
     data: {ds: dirSearchJob},
     success: function (data, textStatus, jqXHR) {
       searchWorker = setTimeout(function () { check_replace_status(data.task_id, data.dsid) }, 500);
     },
     error: function (jqXHR, textStatus, errorThrown) {
       alert('Error submitting replace.');
       search_ui('dir_replace');
     }
  });
}

function go_to_line (dp, y1, x1, y2, x2) {
  dp = unescape(dp);
  var range = new Range(y1, x1, y2, x2);
  
  if (dp in tab_paths) {
    $tabs.tabs('select', "#tabs-" + tab_paths[dp].tab);
    var sess = editor_global.getSession();
    //current_search.findAll(sess);
    sess.getSelection().setSelectionRange(range, false);
  }
  
  else {
    get_file(dp, range);
  }
}

function show_line_results (uid) {
  var div = document.getElementById('line_results_' + uid);
  if (div.style.display == 'none') {
    div.style.display = 'block';
  }
  
  else {
    div.style.display = 'none';
  }
}

function replace_next () {
  if (current_range) {
    var sess = editor_global.getSession();
    var input = sess.getTextRange(current_range);
    var replacement = current_search.replace(input, current_replace);
    if (replacement !== null) {
      current_range.end = sess.replace(current_range, replacement);
    }
  }
  
  search_next('forward');
}

function replace_all (sess) {
  if (!sess) {
    sess = editor_global.getSession();
  }
  
  if (current_range) {
    var y = current_range.end.row + 1;
    var x = current_range.start.column;
    editor_global.gotoLine(y, x);
  }
  
  var ranges = current_search.findAll(sess);
  
  if (!ranges.length)
    return;
    
  var selection = editor_global.getSelectionRange();
  editor_global.clearSelection();
  editor_global.selection.moveCursorTo(0, 0);

  editor_global.$blockScrolling += 1;
  for (var i = ranges.length - 1; i >= 0; --i) {
    var input = sess.getTextRange(ranges[i]);
    var replacement = current_search.replace(input, current_replace);
    if (replacement !== null) {
      sess.replace(ranges[i], replacement);
    }
  }
    
  //editor_global.selection.setSelectionRange(selection);
  editor_global.$blockScrolling -= 1;
}

function replace_all_tab () {
  for (dp in tab_paths) {
    replace_all(tab_paths[dp].session);
  }
}

function search_next (way) {
  var back = false;
  
  if (current_range) {
    var y = current_range.end.row + 1;
    var x = current_range.end.column;
    
    if ((current_backwards && way == 'forward') || (!current_backwards && way == 'back')) {
      x = current_range.end.column - 1;
    }
    
    editor_global.gotoLine(y, x);
  }
  
  if ((current_backwards && way == 'forward') || (!current_backwards && way == 'back')) {
    back = true;
  }
  
  var opts = {
    needle: search_options['needle'],
    backwards: back,
    wrap: search_options['wrap'],
    caseSensitive: search_options['sensitive'],
    wholeWord: search_options['whole'],
    scope: Search.ALL,
    regExp: search_options['regex']
  }
  
  if (current_search) {
    current_search.set(opts);
  }
  
  else {
    current_search = new Search().set(opts);
  }
  
  current_range = current_search.find(editor_global.getSession());
  if (current_range) {
    editor_global.getSession().getSelection().setSelectionRange(current_range, false);
  }
  
  else {
    alert("The search of a thousand miles has completed. Good Job! You Rock!");
  }
}

function choose_search_dir () {
  dir_win.center();
  dir_win.open();
  document.getElementById("dir_chooser_dialog").value = '';
  
  return false;
}

function choose_me (d) {
  d = unescape(d);
  
  var v = document.getElementById("dir_chooser_dialog").value;
  if (v == d) {
    document.getElementById("picked_dir").value = d;
    dir_win.close();
  }
  
  else {
    document.getElementById("dir_chooser_dialog").value = d;
  }
}

function choose_dir_ok () {
  var v = document.getElementById("dir_chooser_dialog").value;
  document.getElementById("picked_dir").value = v;
  dir_win.close();
}

function quick_searcher (e) {
  var n = $('#quick_search').val();
  if (n) {
    var opts = {
      needle: n,
      backwards: false,
      wrap: true,
      caseSensitive: false,
      wholeWord: false,
      scope: Search.ALL,
      regExp: false
    }
    
    var qsearch = new Search().set(opts);
    
    var qrange = qsearch.find(editor_global.getSession());
    if (qrange) {
      editor_global.getSession().getSelection().setSelectionRange(qrange, false);
    }
  }
}

var dir_win;
$(document).ready(function () {
  dir_win = $("#dir_chooser").kendoWindow({title: 'Choose A Directory', modal: true, width: "400px", height: '370px'}).data("kendoWindow");
  $('#dir_chooser > div.browser').fileTree({ root: '', script: '/dirchooser/', expandSpeed: 200, collapseSpeed: 200 }, get_file);
  
  $("#quick_search").keyup(quick_searcher);
});

