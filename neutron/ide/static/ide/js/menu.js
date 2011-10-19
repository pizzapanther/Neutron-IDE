
function about () {
  alert('Neutron IDE v11.11 by Paul M Bailey - paul.m.bailey@gmail.com\n\nneutronide.com\n\nLicense: GPLv3');
}

function SaveAll () {
  $( "#saveall" ).dialog({
  	title: 'Save All',
    modal: true,
    closeOnEscape: false,
    open: function(event, ui) {
      $(this).parent().children().children('.ui-dialog-titlebar-close').hide();
    },
	});
  
  for (dp in tab_paths) {
    var contents = tab_paths[dp].editor.getSession().getValue();
    
    $("#saveall").empty();
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
          $("#saveall").dialog('close');
        }
      },
      error: function (jqXHR, textStatus, errorThrown) { alert('Error Saving: ' + dp); $("#status").html(''); },
    });
  }
}