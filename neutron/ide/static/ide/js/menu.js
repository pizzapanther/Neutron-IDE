
function about () {
  alert('Neutron IDE v12.01 by Paul M Bailey - paul.m.bailey@gmail.com\n\nneutronide.com\n\nLicense: BSD');
  hide_menu();
}

function show_menu () {
  var offset = $("#menu_button").offset();
  $("#main_menu").css('display', 'block');
  $("#main_menu").offset({top: offset.top + 7, left: offset.left + 7});
  return false;
}

function hide_menu () {
  $("#main_menu").css('display', 'none');
  return true;
}

var pref_win;
var save_win;
$(document).ready(function () {
  pref_win = $("#editor_pref").kendoWindow({title: 'Editor Preferences', modal: true, width: "600px"}).data("kendoWindow");
  save_win = $("#saveall").kendoWindow({title: 'Save All', modal: true, width: "400px", height: '200px', actions: false}).data("kendoWindow");
  
  //$(this).parent().children().children('.ui-dialog-titlebar-close').hide();
  
});

function show_pref () {
  hide_menu();
  pref_win.center();
  pref_win.open();
  $("#editor_pref iframe").attr('src', '/editor_pref/');
}

function update_prefs (new_prefs) {
  pref_win.close();
  pref = new_prefs;
  set_all_pref();
}

function CloseAll () {
  if (confirm('Are you sure you wish to close all tabs?')) {
    $('#tabs span.ui-icon-close').click();
  }
}

function SaveAll () {
  save_win.center();
  save_win.open();
  
  $("#saveall").css('display', 'block');
  $("#saveall").empty();
  for (dp in tab_paths) {
    var contents = tab_paths[dp].session.getValue();
    
    $("#saveall").append('<p id="saveall_' + tab_paths[dp].uid + '">Saving ' + tab_paths[dp].filename + ' ...</p>');
    
    $.ajax({
      type: 'POST',
      url: '/filesave/',
      data: {'path': dp, 'contents': contents},
      success: function (data, textStatus, jqXHR) {
        $("#saveall_" + data.uid).remove();
        if (data.result == 'bad') {
          alert(data.error);
        }
        
        if ($('#saveall').children().size() == 0) {
          save_win.close();
        }
      },
      error: function (jqXHR, textStatus, errorThrown) { alert('Error Saving: ' + dp); $("#status").html(''); },
    });
  }
}

canon.addCommand({
    name: 'SaveFile',
    bindKey: {
      win: 'Ctrl-shift-S',
      mac: 'Command-shift-S',
      sender: 'editor'
    },
    exec: function(env, args, request) { SaveAll(); }
});
