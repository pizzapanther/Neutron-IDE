
function wsopen (evt) {
  ws.send(JSON.stringify({'action': 'start', lines: LINES, cols: COLS}));
};

function wsmessage (evt) {
  var data = $.parseJSON(evt.data);
  
  if (data.action == 'update') {
    read_return(data.data)
  }
};

function read_return (data) {
  $('span.cursor').removeClass('cursor');
  
  for (i=0; i < LINES; i++) {
    if (data.lines[i]) {
      var html = '';
      for (j=0; j < data.lines[i].length; j++) {
        classes = 'fg' + data.lines[i][j][1] + ' bg' + data.lines[i][j][2] + ' ';
        if (data.lines[i][j][3]) { classes = classes + 'b '; }
        if (data.lines[i][j][4]) { classes = classes + 'i '; }
        if (data.lines[i][j][5]) { classes = classes + 'u '; }
        if (data.lines[i][j][6]) { classes = classes + 's '; }
        if (data.lines[i][j][7]) { classes = classes + 'r '; }
        
        html = html + '<span class="' + classes + '">' + data.lines[i][j][0] + '</span>';
      }
      
      $('#line' + i).html(html);
    }
  }
  
  if (data.cursor) {
    var col = data.cx + 1;
    $('#line' + data.cy + ' span:nth-child(' + col + ')').addClass('cursor');
  }
}

var COLS;
var LINES;
function terminal_write (ch) {
  var data = {
    action: 'write',
    write: btoa(ch)
  };
  
  ws.send(JSON.stringify(data));
}

function keyme (event, noenter, prevent) {
  if (noenter) {
    if (event.which != 13) {
      var ch = filter_key(event);
      terminal_write(ch);
    }
  }
  
  else {
    var ch = filter_key(event);
    terminal_write(ch);
  }
  
  if (prevent) {
    event.preventDefault();
  }
  
  return false;
}

function init_term () {
  $('#term_input').keypress(function (event) { keyme(event, false, true); });
  $('#term_input').keyup(function (event) { keyme(event, true, true); });
  $('#term_input').keydown(function (event) { keyme(event, true, false); });
  
  $('#term_input').focus(function (event) {
    $('#terminal').removeClass('outline');
  });
  $('body').blur(function (event) {
    $('#terminal').addClass('outline');
  });
  
  $("#term_input").bind('paste', function(e) {
    setTimeout(function () {
      var data = $('#term_input').val();
      terminal_write(data);
      $('#term_input').val('');
    }, 0);
  });
  
  $('#term_input').focus();
  
  calc_term_size();
  resize_term();
}

function resize_term () {
  var html = '';
  for (i=0; i < LINES; i++) {
    html = html + '<div id="line' + i + '"><span> </span></div>'
  }
  $("#terminal").html(html);
}

function calc_term_size () {
  var page_w = $(window).width() - 4;
  var page_h = $(window).height() - 4;
  
  var char_w = $('#terminal span').width();
  var char_h = $('#terminal div').outerHeight();
  
  COLS = Math.floor(page_w / char_w);
  LINES = Math.floor(page_h / char_h);
}

function filter_key (event) {
  ch = event.charCode;
	if (event.ctrlKey) {
		ch = String.fromCharCode(event.keyCode - 64);
		return ch;
	}

	if (!ch && event.keyCode >= 112 && event.keyCode <= 123) { // F1-F12
	    ch = '\x1b' + (event.keyCode - 111);
	    return ch;
	}

	if (ch) {
		if (event.ctrlKey) {
			ch = String.fromCharCode(ch - 96);
		} else {
			ch = String.fromCharCode(ch);
			if (ch == '\r')
				ch = '\n';
		}
	} else {
		switch (event.keyCode) {
		    case 8:
			ch = '\b';
			break;
		    case 9:
			ch = '\t';
			break;
		    case 13:
		    case 10:
			ch = '\r';
			break;
		    case 38:
				ch = '\x1b[A';
			break;
		    case 40:
				ch = '\x1b[B';
			break;
		    case 39:
				ch = '\x1b[C';
			break;
		    case 37:
				ch = '\x1b[D';
			break;
		    case 46:
			ch = '\x1b[3~';
			break;
		    case 35: //end
			ch = '\x1b[F';
			break;
		    case 36: //home
		    ch = '\x1b[H';
			break;
		    case 34: //pgup
		    ch = '\x1b[6~';
			break;
		    case 33: //pgdown
		    ch = '\x1b[5~';
			break;
		    case 27:
			ch = '\x1b';
			break;
		    default:
			return '';
		}
	}
	
  if (event.keyCode == 9) {
    event.preventDefault();
  }
  
	return ch;
}
