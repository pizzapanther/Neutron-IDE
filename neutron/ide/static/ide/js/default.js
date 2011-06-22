$(document).ajaxSend(function(event, xhr, settings) {
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

var tab_counter = 1;
var $tabs = null;
var load_data = "";

$(document).ready( function() {
    $('#file_browser').fileTree({ root: '', script: '/filetree/', expandSpeed: 200, collapseSpeed: 200 }, function(file) {
        $.post('/fileget/', {f: file}, function(data) {
          if (data.fileType == 'text') {
            load_data = data.data;
            $tabs.tabs("add", "#tabs-" + tab_counter, data.filename);
            var editor = ace.edit("editor_" + tab_counter);
            var h = $("#tabs").height() - 29;
            $("#editor_" + tab_counter).css('height', h + 'px');
            editor.resize();
            tab_counter++;
          }
          
          else if (data.fileType == 'binary') {
            alert('binary file');
          }
        });
    });
    
    $tabs = $("#tabsinner").tabs({
      tabTemplate: "<li><a href='#{href}'>#{label}</a> <span class='ui-icon ui-icon-close'>Remove Tab</span></li>",
			add: function( event, ui) {
          $(ui.panel).append( "<div class=\"editor\" id=\"editor_" + tab_counter + "\">" + load_data + "</div>" );
        }
      });
      $tabs.find( ".ui-tabs-nav" ).sortable({ axis: "x" });
});

var myLayout;
  
$(document).ready(function () {
  myLayout = $('body').layout({north__resizable: false, north__closable: false});
});
