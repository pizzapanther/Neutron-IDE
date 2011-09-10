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
  var href = $("ul.ui-tabs-nav li.ui-tabs-selected a").attr('href');
  var cnt = split_href(href);
  return tab_counts[cnt];
}

function SaveCurrentTab () {
  var dp = CurrentTab();
  var contents = tab_paths[dp].editor.getSession().getValue();
  
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

function create_tab (data) {
  if (data.path in tab_paths) {
    $tabs.tabs('select', "#tabs-" + tab_paths[data.path].tab);
  }
  
  else {
    if (data.fileType == 'text') {
      $tabs.tabs("add", "#tabs-" + tab_counter, data.filename);
      $tabs.tabs('select', "#tabs-" + tab_counter);
      
      var editor = ace.edit("editor_" + tab_counter);
      editor.setTheme("ace/theme/" + pref.theme);
      editor.setHighlightActiveLine(pref.hactive);
      
      if (data.mode) {
        var Mode = require("ace/mode/" + data.mode).Mode;
        editor.getSession().setMode(new Mode());
      }
      
      editor.getSession().setTabSize(pref.tabsize);
      editor.getSession().setUseSoftTabs(pref.softab);
      
      var h = $("#tabs").height() - 29;
      $("#editor_" + tab_counter).css('height', h + 'px');
      editor.resize();
      editor.getSession().setValue(data.data);
      
      tab_paths[data.path] = {tab: tab_counter, editor: editor, filename: data.filename}
      tab_counts[tab_counter] = data.path
      
      tab_counter++;
      
      current_edit(data.path);
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
  var dp = CurrentTab();
  current_edit(dp);
  
  var href = $("ul.ui-tabs-nav li.ui-tabs-selected a").attr('href');
  var cnt = split_href(href);
  
  var h = $("#tabs").height();
  $("#editor_" + cnt).height(h - 29);
  try {
    tab_paths[dp].editor.resize();
  }
  
  catch (e) {}
}

function split_href (href) {
  var cnt = href.split('-');
  return cnt[cnt.length - 1];
}

function remove_tab (ui) {
  $("#current_edit").html('');
  
  var cnt = split_href(ui.tab.href);
  var dp = tab_counts[cnt];
  delete tab_paths[dp];
  delete tab_counts[cnt];
  
  try {
    var dp = CurrentTab();
    current_edit(dp);
  }
  
  catch (e) {}
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

var isCtrl = false;

$(document).keyup(function (e) {
	if(e.which == 17) isCtrl=false;
}).keydown(function (e) {
	if(e.which == 17) isCtrl=true;
	if(e.which == 83 && isCtrl == true) {
		SaveCurrentTab();
		return false;
	}
});

function file_browser () {
  $('#file_browser').fileTree({ root: '', script: '/filetree/', expandSpeed: 200, collapseSpeed: 200 }, function(file) {
    $.post('/fileget/', {f: file}, create_tab);
  });
}

$(document).ready( function() {
    file_browser();
    
    $tabs = $("#tabsinner").tabs({
      tabTemplate: "<li><a href='#{href}'>#{label}</a> <span class='ui-icon ui-icon-close'>Remove Tab</span></li>",
      show: function( event, ui) { resize_editor(); },
			add: function( event, ui) {
        $(ui.panel).append( "<div class=\"editor\" id=\"editor_" + tab_counter + "\"></div>" );
      },
      remove: function (event, ui) { remove_tab(ui); }
    });
    $tabs.find( ".ui-tabs-nav" ).sortable({ axis: "x" });
    $( "#tabs span.ui-icon-close" ).live( "click", function() {
      var p = $(this).parent();
      var index = $( "li", $tabs ).index(p);
      $tabs.tabs( "remove", index );
    });
});

var myLayout;
  
$(document).ready(function () {
  myLayout = $('body').layout({onresize_end: resize_editor, north__resizable: false, north__closable: false});
});

window.onbeforeunload = function() {
    return 'Are you sure you wish to leave this page?';
}
