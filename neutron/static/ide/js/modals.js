function new_stuff (d, dir, did) {
  close_right(did);
  var s = "#new_stuff";
  $(s).attr('title', "New File/Dir: " + d);
  $(s).dialog({width: 500, modal: true});
  $("#ui-dialog-title-new_stuff").html("New File/Dir: " + d);
  $('#span_new_upload_file').html('');
  
  $("#create_new_dpath").val(dir);
  $("#create_new_did").val(did);
  
  $(s + ' input').attr("disabled", "");
  
  $("#new_file").focus();
}

function create_new () {
  $('#new_stuff input').attr("disabled", "disabled");
  var new_type = $('input:radio[name=new_type]:checked').val();
  
  if (new_type == 'up') {
    uploadFile('new_upload_file', function (evt) {
      var data = $.parseJSON(evt.target.responseText);
      $("#temp_file").val(data.message);
      do_create_ajax();
    })
  }
  
  else {
    do_create_ajax();
  }
  
  return false;
}

function do_create_ajax () {
  var dpath = $("#create_new_dpath").val();
  var new_type = $('input:radio[name=new_type]:checked').val();
  var name = $("#new_file").val();
  var temp_file = $("#temp_file").val();
  
  $.ajax({
     type: "POST",
     dataType: 'json',
     url: "/new/",
     data: {dir: dpath, new_type: new_type, name: name, temp_file: temp_file},
     success: function (data, textStatus, jqXHR) {
       create_new_ret(data);
     },
     error: function (jqXHR, textStatus, errorThrown) {
       alert('Error creating new file/directory.');
     }
  });
}

function create_new_ret (data) {
  if (data.result) {
    var did = $("#create_new_did").val();
    refresh_dir(did);
    $('#new_stuff').dialog('close');
  }
  
  else {
    alert(data.message);
    $('#new_stuff input').attr("disabled", "");
  }
}

function close_right (did) {
  $('#' + did + '_right').css('display', 'none');
}

function refresh_dir (did) {
  close_right(did);
  if (did == 'file_browser') {
    file_browser();
  }
  
  else {
    $('#' + did + ' > a').click();
    $('#' + did + ' > a').click();
  }
}

function show_new_fn () {
  $("#new_filename").css('display', 'block');
  $("#new_upload").css('display', 'none');
}

function show_new_upload () {
  $("#new_filename").css('display', 'none');
  $("#new_upload").css('display', 'block');
}

function delete_me (path, did) {
  if (confirm('Are you sure you want to delete: ' + path + '?')) {
    $.ajax({
       type: "POST",
       dataType: 'json',
       url: "/delete/",
       data: {dir: path},
       success: function (data, textStatus, jqXHR) {
         refresh_dir(data.message);
       },
       error: function (jqXHR, textStatus, errorThrown) {
         alert('Error deleting ' + path);
       }
    });
  }
  
  close_right(did);
}

function rename (path, did) {
  var tmp = path.split("/");
  if (tmp[tmp.length - 1] == '') {
    var name = tmp[tmp.length - 2];
  }
  
  else {
    var name = tmp[tmp.length - 1];
  }
  
  var newname = prompt('Rename', name);
  if (newname) {
    $.ajax({
       type: "POST",
       dataType: 'json',
       url: "/rename/",
       data: {dir: path, name: newname},
       success: function (data, textStatus, jqXHR) {
         if (data.result) {
          refresh_dir(data.message);
         }
         
         else {
           alert(data.message);
         }
       },
       error: function (jqXHR, textStatus, errorThrown) {
         alert('Error renaming ' + path);
       }
    });
  }
  close_right(did);
}
