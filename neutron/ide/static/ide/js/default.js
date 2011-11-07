function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

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
  $('head').append('<link rel="stylesheet" href="' + static_url + 'ide/css/kendo.' + pref.uitheme + '.css" id="kendoStyle" type="text/css" />');
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
      url: static_url + 'ide/js/ace/theme-' + pref.theme + '.js',
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

function create_tab (data) {
  if (data.path in tab_paths) {
    $tabs.tabs('select', "#tabs-" + tab_paths[data.path].tab);
  }
  
  else {
    if (data.fileType == 'text') {
      $tabs.tabs("add", "#tabs-" + tab_counter, data.filename);
      $tabs.tabs('select', "#tabs-" + tab_counter);
      
      if (!editor_global) {
        editor_global = ace.edit("editor_global");
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

function resize_editor () {
  var edith = $(window).height() - 33;
  
  ksplitter.size("#neutron_body", edith + "px");
  $("#splitter, #splitter > div").height(edith - 2);
  //$("#status").html(edith);
  
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
  
  var h = $("#splitter_right").height();
  $("#editor_global").height(h - $('.ui-widget-header').outerHeight());
  $("#editor_global").width($("#splitter_right").width());
  
  if (editor_global) {
    editor_global.resize();
    editor_global.focus();
  }
}

function split_href (href) {
  var cnt = href.split('-');
  return cnt[cnt.length - 1];
}

function remove_tab (ui) {
  $("#current_edit").html('');
  
  var cnt = split_href(ui.tab.href);
  var dp = tab_counts[cnt];
  
  tab_paths[dp].session.$stopWorker();
  delete tab_paths[dp].session;
  delete tab_paths[dp];
  delete tab_counts[cnt];
  
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

function get_file (file) {
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
      success: create_tab,
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
$(document).ready( function() {
    file_browser();
    
    $tabs = $("#tabsinner").tabs({
      tabTemplate: "<li><a href='#{href}'>#{label}</a> <span class='ui-icon ui-icon-close'><sup>x</sup></span></li>",
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

var ksplitter;
var tabstrip;

$(document).ready(function () {
  ksplitter = $("#neutron_ui").kendoSplitter({
    panes: [{resizable: false, size: '35px', scrollable: false}, {scrollable:false, resizable: false, size: '311px'}],
    orientation: 'vertical'
  }).data("kendoSplitter");
  
  $("#splitter").kendoSplitter({panes: [{collapsible: true, size: '250px'}, {scrollable: false}]});
  
  if (pref.save_session) {
    for (i in init_session) {
      get_file(init_session[i]);
    }
    
    skip_session = false;
  }
  
  //$(window).unbind();
  $(window).resize(resize_editor);
  resize_editor();
});

window.onbeforeunload = function() {
    return 'Leaving so soon!';
}

var canon = require('pilot/canon');

canon.addCommand({
    name: 'SaveFile',
    bindKey: {
      win: 'Ctrl-S',
      mac: 'Command-S',
      sender: 'editor'
    },
    exec: function(env, args, request) { SaveCurrentTab(); }
});



