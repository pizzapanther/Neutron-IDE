$(document).ajaxSend(function(event, xhr, settings) {
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    
    if (track_ajax) {
      _gaq.push(['_trackPageview', settings.url.split("?")[0]]);
    }
    
    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

var tab_counter = 0;
var $tabs = null;
var load_data = "";
var tab_paths = {};
var tab_counts = {};
var track_int = 600000;

function CurrentTab () {
  try  {
    var href = $("ul.ui-tabs-nav li.ui-tabs-selected a").attr('href');
    var cnt = split_href(href);
    return tab_counts[cnt];
  }
  
  catch (e) {
    return false;
  }
}

function SaveCurrentTab () {
  var dp = CurrentTab();
  var contents = editor_global.getSession().getValue();
  
  $("#status").html('Saving ' + tab_paths[dp].filename);
  
  $.ajax({
    type: 'POST',
    url: '/filesave/',
    data: {'path': dp, 'contents': contents},
    success: function (data, textStatus, jqXHR) {
      $("#status").html('');
      if (data.result == 'bad') {
        alert(data.error);
      }
    },
    error: function (jqXHR, textStatus, errorThrown) { alert('Error Saving: ' + dp); $("#status").html(''); },
  });
}

function set_all_pref () {
  for (dp in tab_paths) {
    set_edit_pref(tab_paths[dp].session, "editor_" + tab_paths[dp].tab);
  }
  
  $("#kendoStyle").remove();
  $('head').append('<link rel="stylesheet" href="' + static_url + 'ide/css/kendo_styles/kendo.' + pref.uitheme + '.min.css" id="kendoStyle" type="text/css" />');
}

function set_edit_pref (sess, id) {
  load_theme = true;
  for (i in loaded_themes) {
    if (loaded_themes[i] == pref.theme) {
      load_theme = false;
      break;
    }
  }
  
  if (load_theme) {
    $.ajax({
      url: static_url + 'ide/js/ace/build/src/theme-' + pref.theme + '.js',
      dataType: "script",
      async: false,
    });
    loaded_themes.push(pref.theme);
  }
  
  editor_global.setTheme("ace/theme/" + pref.theme);
  
  var handler = null;
  if (pref.keybind == 'emacs') {
    handler = require("ace/keyboard/keybinding/emacs").Emacs;
  }
  
  else if (pref.keybind == 'vim') {
    handler = require("ace/keyboard/keybinding/vim").Vim;
  }
  
  editor_global.setKeyboardHandler(handler);
  
  editor_global.setHighlightActiveLine(pref.hactive);
  editor_global.setHighlightSelectedWord(pref.hword);
  editor_global.setShowInvisibles(pref.invisibles);
  editor_global.setBehavioursEnabled(pref.behave);
  
  editor_global.renderer.setShowGutter(pref.gutter);
  editor_global.renderer.setShowPrintMargin(pref.pmargin);
  
  sess.setTabSize(pref.tabsize);
  sess.setUseSoftTabs(pref.softab);
  
  switch (pref.swrap) {
    case "off":
      sess.setUseWrapMode(false);
      editor_global.renderer.setPrintMarginColumn(80);
      break;
      
    case "40":
      sess.setUseWrapMode(true);
      sess.setWrapLimitRange(40, 40);
      editor_global.renderer.setPrintMarginColumn(40);
      break;
      
    case "80":
      sess.setUseWrapMode(true);
      sess.setWrapLimitRange(80, 80);
      editor_global.renderer.setPrintMarginColumn(80);
      break;
      
    case "free":
      sess.setUseWrapMode(true);
      sess.setWrapLimitRange(null, null);
      editor_global.renderer.setPrintMarginColumn(80);
      break;
  }
  
  $("#" + id).css('font-size', pref.fontsize);
}

var editor_global = null;
var EditSession = require('ace/edit_session').EditSession;
var UndoManager = require("ace/undomanager").UndoManager;

function create_tab (data, textStatus, jqXHR, range) {
  if (data.path in tab_paths) {
    $tabs.tabs('select', "#tabs-" + tab_paths[data.path].tab);
  }
  
  else {
    if (data.fileType == 'text') {
      $tabs.tabs("add", "#tabs-" + tab_counter, data.filename);
      $tabs.tabs('select', "#tabs-" + tab_counter);
      
      if (!editor_global) {
        editor_global = ace.edit("editor_global");
        add_commands(editor_global);
      }
      
      var sess = new EditSession(data.data); 
      sess.setUndoManager(new UndoManager());
      editor_global.setSession(sess);
      
      if (data.mode) {
        var Mode = require("ace/mode/" + data.mode).Mode;
        sess.setMode(new Mode());
      }
      
      set_edit_pref(sess, "editor_" + tab_counter);
      
      editor_global.resize();
      editor_global.focus();
      
      tab_paths[data.path] = {tab: tab_counter, session: sess, filename: data.filename, uid: data.uid}
      tab_counts[tab_counter] = data.path
      
      tab_counter++;
      
      current_edit(data.path);
      
      if (pref.save_session) {
        save_session();
      }
      
      if (range) {
        sess.getSelection().setSelectionRange(range, false);
      }
    }
    
    else if (data.fileType == 'binary') {
      alert('binary file');
    }
  }
}

function current_edit (path) {
  try {
    path = path.replace(basedir + '/', '');
    
    $("#current_edit").html(path);
  }
  
  catch (e) {}
}

function resize_editor (skip_splitter) {
  var edith = $(window).height() - 33;
  
  ksplitter.size("#neutron_body", edith + "px");
  $("#splitter, #splitter > div").height(edith - 2);
  
  var nbw = $("#neutron_body").width() + 1;
  $("#neutron_body").width(nbw);
  
  var dp = CurrentTab();
  if (dp) {
    current_edit(dp);
    if (tab_paths[dp]) {
      editor_global.setSession(tab_paths[dp].session);
    }
    
    var href = $("ul.ui-tabs-nav li.ui-tabs-selected a").attr('href');
    var cnt = split_href(href);
  }
  
  if (tsplitter) {
    var h = $("#ide_top").height() - 2;
  }
  
  else {
    var h = $("#splitter_right").height();
  }
  
  $("#editor_global").height(h - $('.ui-widget-header').outerHeight());
  $("#editor_global").width($("#splitter_right").width());
  
  if (editor_global) {
    editor_global.resize();
    editor_global.focus();
  }
  
  else {
    
  }
  
  resize_tabs();
}

function resize_tabs () {
  var h = $('#tooltabs').height();
  var t = $('#tooltabs > ul').height() + 2;
  
  $("#tooltabs > div").height(h - t);
}

function split_href (href) {
  var cnt = href.split('-');
  return cnt[cnt.length - 1];
}

function remove_tab (ui) {
  $("#current_edit").html('');
  
  var cnt = split_href(ui.tab.href);
  var dp = tab_counts[cnt];
  
  if (tab_paths[dp] && tab_paths[dp].session) {
    tab_paths[dp].session.$stopWorker();
    delete tab_paths[dp].session;
    delete tab_paths[dp];
  }
  
  if (tab_counts[cnt]) {
    delete tab_counts[cnt];
  }
  
  if (pref.save_session) {
    save_session();
  }
  
  var dp = CurrentTab();
  if (dp) {
    current_edit(dp);
    resize_editor();
  }
  
  else {
    editor_global = null;
    $('#editor_global').html('');
  }
}

function uploadProgress(id, evt) {
  if (evt.lengthComputable) {
    var pc = Math.round(evt.loaded * 100 / evt.total);
    
    $('#span_' + id).html('Uploading ' + pc + '%');
  }
}

function uploadFile(id, onComplete) {
  var xhr = new XMLHttpRequest();
  var fd = document.getElementById(id).files[0];
  
  xhr.upload.addEventListener("progress", function (evt) { uploadProgress(id, evt); }, false);
  xhr.addEventListener("load", function (evt) { onComplete(evt); }, false);
  xhr.addEventListener("error", function (evt) { alert('Upload Failed'); }, false);
  xhr.addEventListener("abort", function (evt) { alert('Upload Cancel'); }, false);
  
  xhr.open("POST", "/temp_file/?name=" + encodeURIComponent(fd.fileName));
  xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
  xhr.send(fd);
}

function get_file (file, range) {
  var img_patt = /\.(jpg|jpeg|png|bmp|pxd)$/i;
  
  if (img_patt.test(file)) {
    window.open('/external_open' + encodeURI(file), '_blank');
  }
  
  else {
    $.ajax({
      type: 'POST',
      async: false,
      url: '/fileget/',
      data: {f: file},
      success: function (data, textStatus, jqXHR) {create_tab(data, textStatus, jqXHR, range);},
      error: function (jqXHR, textStatus, errorThrown) { alert('Error Opening: ' + file); },
    });
  }
}

function file_browser () {
  $('#file_browser > div.inner').fileTree({ root: '', script: '/filetree/', expandSpeed: 200, collapseSpeed: 200 }, get_file);
}

function save_session () {
  if (skip_session) {}
  
  else {
    var files = '';
    $("ul.ui-tabs-nav > li > a").each(function (index, ele) {
      var cnt = split_href(ele.href);
      var dp = tab_counts[cnt];
      files = files + dp + "\n";
    });
    
    files = files.substring(0, files.length-1);
    
    $.ajax({
      type: 'POST',
      url: '/save_session/',
      data: {'files': files},
      success: function (data, textStatus, jqXHR) {},
      error: function (jqXHR, textStatus, errorThrown) { alert('Error Saving Session'); },
    });
  }
}

function sort_change (event, ui) {
  if (pref.save_session) {
    save_session();
  }
}

var stopMiddle = false;
function middleClick (e, ele) {
  if (e && e.button == 1) {
    if (stopMiddle) {
      stopMiddle = false;
    }
    
    else {
      var p = $(ele).parent();
      
      if ($(p).hasClass('ui-tabs-selected')) {
        stopMiddle = true;
      }
      
      var index = $("li", $tabs ).index(p);
      $tabs.tabs("remove", index );
      
      return false;
    }
  }
  
  return true;
}

$(document).ready( function() {
    file_browser();
    
    $tabs = $("#tabsinner").tabs({
      tabTemplate: "<li><a class='middle' href='#{href}' onclick='return middleClick(event, this)'>#{label}</a> <span class='ui-icon ui-icon-close'><sup>x</sup></span></li>",
      show: function( event, ui) { resize_editor(); },
			add: function( event, ui) {
        $(ui.panel).append( "<div class=\"editor\" id=\"editor_" + tab_counter + "\"></div>" );
      },
      remove: function (event, ui) { remove_tab(ui); }
    });
    $tabs.find( ".ui-tabs-nav" ).sortable({ axis: "x", update: sort_change});
    $( "#tabs span.ui-icon-close" ).live( "click", function() {
      var p = $(this).parent();
      var index = $( "li", $tabs ).index(p);
      $tabs.tabs( "remove", index );
    });
    
});

function size_search (e) {
  setTimeout(function () {
    var width = $("#splitter_left").width() - 83;
    $("#search_panel_results a.expand").width(width);
    
    $("#editor_global").width($("#splitter_right").width());
    
    if (tsplitter) {
      var old_total = 5 + $("#ide_top").height() + $("#ide_bottom").height();
      var new_total = $("#splitter_right").height();
      
      if (new_total - old_total != 0) {
        $("#ide_top").height(new_total - (5 + $("#ide_bottom").height()));
      }
      
      var h = $("#ide_top").height() - 2;
      $("#editor_global").height(h - $('.ui-widget-header').outerHeight());
      
      if (window.send_resize) {
        if ($("#ide_bottom").height() > 0) {
          send_resize();
        }
      }
      
    }
    
    if (editor_global) {
      editor_global.resize();
    }
    
  }, 400);
}

var ksplitter;
var esplitter;
var tsplitter;
var tabstrip;
var tooltabs;
var search_panel;

$(document).ready(function () {
  $("body").click(function (eObj) {
    $('.right_menu').css('display', 'none');
    
    if (eObj.target.id && eObj.target.id == 'menu_button') {}
    else if (eObj.target.parentElement && eObj.target.parentElement.id && eObj.target.parentElement.id == 'menu_button') {}
    else {
      hide_menu();
    }
  });
  
  search_panel = $("#search_panel").kendoPanelBar().data("kendoPanelBar");
  $("#search_panel_search > span").click();
  
  tooltabs = $("#tooltabs").kendoTabStrip({animation: false}).data("kendoTabStrip");
  tooltabs.select("#fbtab");
  $("#tooltabs > ul li").click(resize_tabs);
  
  ksplitter = $("#neutron_ui").kendoSplitter({
    panes: [{resizable: false, size: '35px', scrollable: false}, {scrollable:false, resizable: false, size: '311px'}],
    orientation: 'vertical'
  }).data("kendoSplitter");
  
  esplitter = $("#splitter").kendoSplitter({resize: size_search, panes: [{collapsible: true, size: '250px', scrollable: false}, {scrollable: false}], resize: size_search}).data("kendoSplitter");
  
  if (splitterm) {
    setTimeout(
      function () {
        tsplitter = $("#splitter_right").kendoSplitter({orientation: 'vertical', resize: size_search, panes: [{collapsible: false, scrollable: false}, {contentUrl: "/terminal/?split=1", resizable: true, collapsible: true, scrollable: false, size: '300px'}]}).data("kendoSplitter");
      },
      0
    )
  }
  
  if (pref.save_session) {
    for (i in init_session) {
      get_file(init_session[i]);
    }
    
    skip_session = false;
  }
  
  //$(window).unbind();
  $(window).resize(resize_editor);
  resize_editor();
  
  if (track_ajax) {
    setTimeout(track_ide, track_int);
  }
  //Implementation of autoSave
    var autoSavePending = false;
    
      editor_global.getSession().on('change', function(){
        $("#status").html(' ');
        if (autoSavePending == false){
          autoSavePending = true;          
                    
          setTimeout(function(){
            $("#status").html('All Files Auto Saved');  
            doSaveAll();
            autoSavePending = false;
            
          },5000);
          
        }
      });
});

function track_ide () {
  var d = new Date();
  var ts = d.getYear() + '-' + d.getMonth() + '-' + d.getDay() + '-' + d.getHours() + '-' + d.getMinutes();
  _gaq.push(['_trackPageview', "/?ts=" + ts]);
  setTimeout(track_ide, track_int);
}

window.onbeforeunload = function() {
    return 'Leaving so soon!';
}

function add_commands (e) {
  e.commands.addCommand({
      name: 'SaveFile',
      bindKey: {
        win: 'Ctrl-S',
        mac: 'Command-S',
        sender: 'editor'
      },
      exec: function(env, args, request) { SaveCurrentTab(); }
  });
  
  e.commands.addCommand({
      name: 'QuickSearch',
      bindKey: {
        win: 'Ctrl-Q',
        mac: 'Command-Q',
        sender: 'editor'
      },
      exec: function(env, args, request) { $('#quick_search').focus().select(); }
  });
  
  e.commands.addCommand({
    name: 'SaveAllFile',
    bindKey: {
      win: 'Ctrl-shift-S',
      mac: 'Command-shift-S',
      sender: 'editor'
    },
    exec: function(env, args, request) { SaveAll(); }
  });
}
