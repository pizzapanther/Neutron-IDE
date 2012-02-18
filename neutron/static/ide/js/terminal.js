function initws () {
  init_term();
  ws = new WebSocket(wsurl);
  ws.onopen = wsopen;
  ws.onmessage = wsmessage;
  ws.onclose = wsclose;
}
      
$(window).load(initws);

function start_terminal () {
  var ts = new Date().getTime();
  
  terminals[ts] = {};
  
  current_ts = ts;
  terminal_count = terminal_count + 1;
  
  var data = {
    action: 'start',
    lines: LINES,
    cols: COLS,
    tsid: ts,
    session: getCookie(cookie_name)
  }
  
  ws.send(JSON.stringify(data));
  
  var html = '<div class="a term" onclick="view_terminal(' + ts + ')" id="terminal_' + ts +'">\
<div class="n">'+ terminal_count + '</div><img src="' + static_url + 'ide/img/term/terminal_black.png"\
alt="View Terminal '+ terminal_count + '" title="New Terminal '+ terminal_count + '"></div>';
  $('#icons').append(html);
  $('#icons .a.term img').removeClass('selected');
  $('#icons #terminal_' + ts + ' img').addClass('selected');
  $('#reconnect').addClass('hidden');
  $('#term_input').focus();
}

function restart_terminal (tsid) {
  var ts = tsid;
  terminals[ts] = {};
  current_ts = ts;
  terminal_count = terminal_count + 1;
  
  var data = {
    action: 'start',
    lines: LINES,
    cols: COLS,
    tsid: ts,
    session: getCookie(cookie_name),
    restart: true
  }
  
  ws.send(JSON.stringify(data));
  
  var html = '<div class="a term" onclick="view_terminal(' + ts + ')" id="terminal_' + ts +'">\
<div class="n">'+ terminal_count + '</div><img src="' + static_url + 'ide/img/term/terminal_black.png"\
alt="View Terminal '+ terminal_count + '" title="New Terminal '+ terminal_count + '"></div>';
  $('#icons').append(html);
  $('#icons .a.term img').removeClass('selected');
  $('#icons #terminal_' + ts + ' img').addClass('selected');
  $('#reconnect').addClass('hidden');
  $('#term_input').focus();
}

function refresh_full () {
  if (current_ts) {
    var data = {action: 'full', tsid: current_ts};
    ws.send(JSON.stringify(data));
  }
}

function view_terminal (ts) {
  var data = {
    action: 'full',
    tsid: ts,
    lines: LINES,
    cols: COLS
  };
  
  ws.send(JSON.stringify(data));
  
  $('#icons .a.term img').removeClass('selected');
  $('#icons #terminal_' + ts + ' img').addClass('selected');
  
  current_ts = ts;
  $('#term_input').focus();
}

function wsopen (evt) {
  
};

function wsmessage (evt) {
  //var d = new Date();
  //console.log(d);
  //console.log(d.getMilliseconds());
  
  //manually deflate/inflate for speed until tornado supports WebSocket GZip
  var data = $.parseJSON(RawDeflate.inflate(atob(evt.data)));
  
  if (data.action == 'update') {
    read_return(data.data);
  }
  
  else if (data.action == 'message') {
    alert(data.data);
  }
  
  else if (data.action == 'doreset') {
    var data = {action: 'reset', tsid: current_ts};
    ws.send(JSON.stringify(data));
  }
  
  else if (data.action == 'oldterms') {
    for (i = 0; i < data.data.length; i++) {
      restart_terminal(parseInt(data.data[i]));
    }
  }
  
  else if (data.action == 'killed') {
    delete terminals[data.data];
    terminal_count = terminal_count - 1;
    $('#terminal_' + data.data).remove();
    
    if (data.data == current_ts) {
      current_ts = null;
    }
    
    if (terminal_count == 0) {
      $('#reconnect').removeClass('hidden');
    }
    
    else {
      renumber();
      $('.term .n').last().click();
    }
  }
}

function close_current () {
  var data = {action: 'solong', tsid: current_ts};
  ws.send(JSON.stringify(data));
}

function prev_page () {
  var data = {action: 'prev', tsid: current_ts};
  ws.send(JSON.stringify(data));
}

function next_page () {
  var data = {action: 'next', tsid: current_ts};
  ws.send(JSON.stringify(data));
}

function renumber () {
  $('.term .n').each(function(index, ele) {
    $(ele).html(index + 1);
  });
}

function wsclose (evt) {
  terminals = {};
  terminal_count = 0;
  current_ts = null;
  $('#refresh').removeClass('hidden');
}

function select_mode () {
  $('#icons #sel_icon img').toggleClass('selected');
  $('#input_wrapper').toggleClass('selected');
}

function read_return (data) {
  //var count = 0;
  for (i=0; i < LINES; i++) {
    if (data.lines[i]) {
      $('#line' + i).html('<span>' + data.lines[i] +'</span>');
    }
  }
  
  if (data.cursor) {
    var l = char_w * data.cx + 2;
    var t = char_h * data.cy + 2;
    
    $('#cursor').css('display', 'block');
    $('#cursor').css('top', t + 'px');
    $('#cursor').css('left', l + 'px');
  }
  
  else {
    $('#cursor').css('display', 'none');
  }
  
  //console.log('complete');
  //var d = new Date();
  //console.log(d);
  //console.log(d.getMilliseconds());
  //console.log('Count changed:' +  count);
}

var COLS;
var LINES;
var current_ts = null;
function terminal_write (ch) {
  try {
    var data = {
      action: 'write',
      write: ch,
      tsid: current_ts
    };
  }
  
  catch (e) { console.log(e); }
  
  ws.send(JSON.stringify(data));
}

var lastKeyDownEvent;
var lastKeyPressedEvent;
var lastNormalKeyDownEvent;
var catchModifiersEarly;
var crLfMode = false;

function applyModifiers (ch, event) {
  if (ch) {
    if (event.ctrlKey) {
      if (ch >= 32 && ch <= 127) {
        // For historic reasons, some control characters are treated specially
        switch (ch) {
        case /* 3 */ 51: ch  =  27; break;
        case /* 4 */ 52: ch  =  28; break;
        case /* 5 */ 53: ch  =  29; break;
        case /* 6 */ 54: ch  =  30; break;
        case /* 7 */ 55: ch  =  31; break;
        case /* 8 */ 56: ch  = 127; break;
        case /* ? */ 63: ch  = 127; break;
        default:         ch &=  31; break;
        }
      }
    }
    return String.fromCharCode(ch);
  } else {
    return undefined;
  }
}

function vt100_keyPress (event) {
  if (lastKeyDownEvent) {
    lastKeyDownEvent = undefined;
  }
  
  else {
    handleKey(event.altKey || event.metaKey ? fixEvent(event) : event);
  }
  
  event.preventDefault();
  
  lastNormalKeyDownEvent = undefined;
  lastKeyPressedEvent = event;
  return false;
}

function fixEvent (event) {
  if (event.ctrlKey && event.altKey) {
    var fake                = [ ];
    fake.charCode           = event.charCode;
    fake.keyCode            = event.keyCode;
    fake.ctrlKey            = false;
    fake.shiftKey           = event.shiftKey;
    fake.altKey             = false;
    fake.metaKey            = event.metaKey;
    return fake;
  }

  // Some browsers fail to translate keys, if both shift and alt/meta is
  // pressed at the same time. We try to translate those cases, but that
  // only works for US keyboard layouts.
  if (event.shiftKey) {
    var u                   = undefined;
    var s                   = undefined;
    switch (lastNormalKeyDownEvent.keyCode) {
    case  39: /* ' -> " */ u = 39; s =  34; break;
    case  44: /* , -> < */ u = 44; s =  60; break;
    case  45: /* - -> _ */ u = 45; s =  95; break;
    case  46: /* . -> > */ u = 46; s =  62; break;
    case  47: /* / -> ? */ u = 47; s =  63; break;

    case  48: /* 0 -> ) */ u = 48; s =  41; break;
    case  49: /* 1 -> ! */ u = 49; s =  33; break;
    case  50: /* 2 -> @ */ u = 50; s =  64; break;
    case  51: /* 3 -> # */ u = 51; s =  35; break;
    case  52: /* 4 -> $ */ u = 52; s =  36; break;
    case  53: /* 5 -> % */ u = 53; s =  37; break;
    case  54: /* 6 -> ^ */ u = 54; s =  94; break;
    case  55: /* 7 -> & */ u = 55; s =  38; break;
    case  56: /* 8 -> * */ u = 56; s =  42; break;
    case  57: /* 9 -> ( */ u = 57; s =  40; break;

    case  59: /* ; -> : */ u = 59; s =  58; break;
    case  61: /* = -> + */ u = 61; s =  43; break;
    case  91: /* [ -> { */ u = 91; s = 123; break;
    case  92: /* \ -> | */ u = 92; s = 124; break;
    case  93: /* ] -> } */ u = 93; s = 125; break; 
    case  96: /* ` -> ~ */ u = 96; s = 126; break;

    case 109: /* - -> _ */ u = 45; s =  95; break;
    case 111: /* / -> ? */ u = 47; s =  63; break;

    case 186: /* ; -> : */ u = 59; s =  58; break;
    case 187: /* = -> + */ u = 61; s =  43; break;
    case 188: /* , -> < */ u = 44; s =  60; break;
    case 189: /* - -> _ */ u = 45; s =  95; break;
    case 190: /* . -> > */ u = 46; s =  62; break;
    case 191: /* / -> ? */ u = 47; s =  63; break;
    case 192: /* ` -> ~ */ u = 96; s = 126; break;
    case 219: /* [ -> { */ u = 91; s = 123; break;
    case 220: /* \ -> | */ u = 92; s = 124; break;
    case 221: /* ] -> } */ u = 93; s = 125; break; 
    case 222: /* ' -> " */ u = 39; s =  34; break;
    default:                                break;
    }
    if (s && (event.charCode == u || event.charCode == 0)) {
      var fake              = [ ];
      fake.charCode         = s;
      fake.keyCode          = event.keyCode;
      fake.ctrlKey          = event.ctrlKey;
      fake.shiftKey         = event.shiftKey;
      fake.altKey           = event.altKey;
      fake.metaKey          = event.metaKey;
      return fake;
    }
  }
  return event;
}

function handleKey (event) {
  var ch = event.charCode;
  var key = event.keyCode;
  
  // Apply modifier keys (ctrl and shift)
  if (ch) {
    key = undefined;
  }
  
  ch = applyModifiers(ch, event);

  // By this point, "ch" is either defined and contains the character code, or
  // it is undefined and "key" defines the code of a function key 
  if (ch != undefined) {
    //this.scrollable.scrollTop         = this.numScrollbackLines *
    //                                    this.cursorHeight + 1;
  }
  
  else {
    if ((event.altKey || event.metaKey) && !event.shiftKey && !event.ctrlKey) {
      switch (key) {
      case  33: /* Page Up      */ ch = '\u001B<';                      break;
      case  34: /* Page Down    */ ch = '\u001B>';                      break;
      case  37: /* Left         */ ch = '\u001Bb';                      break;
      case  38: /* Up           */ ch = '\u001Bp';                      break;
      case  39: /* Right        */ ch = '\u001Bf';                      break;
      case  40: /* Down         */ ch = '\u001Bn';                      break;
      case  46: /* Delete       */ ch = '\u001Bd';                      break;
      default:                                                          break;
      }
    } else if (event.shiftKey && !event.ctrlKey &&
               !event.altKey && !event.metaKey) {
      switch (key) {
      case  33: /* Page Up      */ this.scrollBack();                   return;
      case  34: /* Page Down    */ this.scrollFore();                   return;
      default:                                                          break;
      }
    }
    if (ch == undefined) {
      switch (key) {
      case   8: /* Backspace    */ ch = '\u007f';                       break;
      case   9: /* Tab          */ ch = '\u0009';                       break;
      case  10: /* Return       */ ch = '\u000A';                       break;
      case  13: /* Enter        */ ch = crLfMode ?
                                        '\r\n' : '\r';                  break;
      case  16: /* Shift        */                                      return;
      case  17: /* Ctrl         */                                      return;
      case  18: /* Alt          */                                      return;
      case  19: /* Break        */                                      return;
      case  20: /* Caps Lock    */                                      return;
      case  27: /* Escape       */ ch = '\u001B';                       break;
      case  33: /* Page Up      */ ch = '\u001B[5~';                    break;
      case  34: /* Page Down    */ ch = '\u001B[6~';                    break;
      case  35: /* End          */ ch = '\u001BOF';                     break;
      case  36: /* Home         */ ch = '\u001BOH';                     break;
      case  37: /* Left         */ ch = this.cursorKeyMode ?
                             '\u001BOD' : '\u001B[D';                   break;
      case  38: /* Up           */ ch = this.cursorKeyMode ?
                             '\u001BOA' : '\u001B[A';                   break;
      case  39: /* Right        */ ch = this.cursorKeyMode ?
                             '\u001BOC' : '\u001B[C';                   break;
      case  40: /* Down         */ ch = this.cursorKeyMode ?
                             '\u001BOB' : '\u001B[B';                   break;
      case  45: /* Insert       */ ch = '\u001B[2~';                    break;
      case  46: /* Delete       */ ch = '\u001B[3~';                    break;
      case  91: /* Left Window  */                                      return;
      case  92: /* Right Window */                                      return;
      case  93: /* Select       */                                      return;
      case  96: /* 0            */ ch = applyModifiers(48, event); break;
      case  97: /* 1            */ ch = applyModifiers(49, event); break;
      case  98: /* 2            */ ch = applyModifiers(50, event); break;
      case  99: /* 3            */ ch = applyModifiers(51, event); break;
      case 100: /* 4            */ ch = applyModifiers(52, event); break;
      case 101: /* 5            */ ch = applyModifiers(53, event); break;
      case 102: /* 6            */ ch = applyModifiers(54, event); break;
      case 103: /* 7            */ ch = applyModifiers(55, event); break;
      case 104: /* 8            */ ch = applyModifiers(56, event); break;
      case 105: /* 9            */ ch = applyModifiers(58, event); break;
      case 106: /* *            */ ch = applyModifiers(42, event); break;
      case 107: /* +            */ ch = applyModifiers(43, event); break;
      case 109: /* -            */ ch = applyModifiers(45, event); break;
      case 110: /* .            */ ch = applyModifiers(46, event); break;
      case 111: /* /            */ ch = applyModifiers(47, event); break;
      case 112: /* F1           */ ch = '\u001BOP';                     break;
      case 113: /* F2           */ ch = '\u001BOQ';                     break;
      case 114: /* F3           */ ch = '\u001BOR';                     break;
      case 115: /* F4           */ ch = '\u001BOS';                     break;
      case 116: /* F5           */ ch = '\u001B[15~';                   break;
      case 117: /* F6           */ ch = '\u001B[17~';                   break;
      case 118: /* F7           */ ch = '\u001B[18~';                   break;
      case 119: /* F8           */ ch = '\u001B[19~';                   break;
      case 120: /* F9           */ ch = '\u001B[20~';                   break;
      case 121: /* F10          */ ch = '\u001B[21~';                   break;
      case 122: /* F11          */ ch = '\u001B[23~';                   break;
      case 123: /* F12          */ ch = '\u001B[24~';                   break;
      case 144: /* Num Lock     */                                      return;
      case 145: /* Scroll Lock  */                                      return;
      case 186: /* ;            */ ch = applyModifiers(59, event); break;
      case 187: /* =            */ ch = applyModifiers(61, event); break;
      case 188: /* ,            */ ch = applyModifiers(44, event); break;
      case 189: /* -            */ ch = applyModifiers(45, event); break;
      case 190: /* .            */ ch = applyModifiers(46, event); break;
      case 191: /* /            */ ch = applyModifiers(47, event); break;
      case 192: /* `            */ ch = applyModifiers(96, event); break;
      case 219: /* [            */ ch = applyModifiers(91, event); break;
      case 220: /* \            */ ch = applyModifiers(92, event); break;
      case 221: /* ]            */ ch = applyModifiers(93, event); break;
      case 222: /* '            */ ch = applyModifiers(39, event); break;
      default:                                                          return;
      }
      //this.scrollable.scrollTop       = this.numScrollbackLines *
      //                                  this.cursorHeight + 1;
    }
  }

  // "ch" now contains the sequence of keycodes to send. But we might still
  // have to apply the effects of modifier keys.
  if (event.shiftKey || event.ctrlKey || event.altKey || event.metaKey) {
    var start, digit, part1, part2;
    if ((start = ch.substr(0, 2)) == '\u001B[') {
      for (part1 = start;
           part1.length < ch.length &&
             (digit = ch.charCodeAt(part1.length)) >= 48 && digit <= 57; ) {
        part1                         = ch.substr(0, part1.length + 1);
      }
      part2                           = ch.substr(part1.length);
      if (part1.length > 2) {
        part1                        += ';';
      }
    } else if (start == '\u001BO') {
      part1                           = start;
      part2                           = ch.substr(2);
    }
    if (part1 != undefined) {
      ch                              = part1                                 +
                                       ((event.shiftKey             ? 1 : 0)  +
                                        (event.altKey|event.metaKey ? 2 : 0)  +
                                        (event.ctrlKey              ? 4 : 0)) +
                                        part2;
    } else if (ch.length == 1 && (event.altKey || event.metaKey)) {
      ch                              = '\u001B' + ch;
    }
    
    if (ch.length == 2 && ch[0] == '\u001B') {
      if (ch[1] == '\u0004') {ch = '\u0004';}
      else if (ch[1] == '\u0012') {ch = '\u0012';}
    }
  }
  
  if (ch) {
    terminal_write(ch);
  }
  //if (this.menu.style.visibility == 'hidden') {
    // this.vt100('R: c=');
    // for (var i = 0; i < ch.length; i++)
    //   this.vt100((i != 0 ? ', ' : '') + ch.charCodeAt(i));
    // this.vt100('\r\n');
    //this.keysPressed(ch);
  //}
}

function vt100_keyUp (event) {
  if (lastKeyPressedEvent) {
    (event.target || event.srcElement).value = '';
  }
  
  else {
    //checkComposedKeys(event);
    
    if (lastNormalKeyDownEvent) {
      //ENABLING EARLY CATCHING OF MODIFIER KEYS
      catchModifiersEarly    = true;
      var asciiKey                =
        event.keyCode ==  32                         ||
        event.keyCode >=  48 && event.keyCode <=  57 ||
        event.keyCode >=  65 && event.keyCode <=  90;
      var alphNumKey              =
        asciiKey                                     ||
        event.keyCode >=  96 && event.keyCode <= 105;
      var normalKey               =
        alphNumKey                                   ||
        event.keyCode ==  59 || event.keyCode ==  61 ||
        event.keyCode == 106 || event.keyCode == 107 ||
        event.keyCode >= 109 && event.keyCode <= 111 ||
        event.keyCode >= 186 && event.keyCode <= 192 ||
        event.keyCode >= 219 && event.keyCode <= 222 ||
        event.keyCode == 252;
      var fake                    = [ ];
      fake.ctrlKey                = event.ctrlKey;
      fake.shiftKey               = event.shiftKey;
      fake.altKey                 = event.altKey;
      fake.metaKey                = event.metaKey;
      if (asciiKey) {
        fake.charCode             = event.keyCode;
        fake.keyCode              = 0;
      } else {
        fake.charCode             = 0;
        fake.keyCode              = event.keyCode;
        if (!alphNumKey && (event.ctrlKey || event.altKey || event.metaKey)) {
          fake                    = fixEvent(fake);
        }
      }
      lastNormalKeyDownEvent = undefined;
      handleKey(fake);
    }
  }

  lastKeyDownEvent           = undefined;
  lastKeyPressedEvent        = undefined;
  return false;
}

function vt100_keyDown (event) {
  //checkComposedKeys(event);
  lastKeyPressedEvent      = undefined;
  lastKeyDownEvent         = undefined;
  lastNormalKeyDownEvent   = event;

  var asciiKey                  =
    event.keyCode ==  32                         ||
    event.keyCode >=  48 && event.keyCode <=  57 ||
    event.keyCode >=  65 && event.keyCode <=  90;
  var alphNumKey                =
    asciiKey                                     ||
    event.keyCode >=  96 && event.keyCode <= 105 ||
    event.keyCode == 226;
  var normalKey                 =
    alphNumKey                                   ||
    event.keyCode ==  59 || event.keyCode ==  61 ||
    event.keyCode == 106 || event.keyCode == 107 ||
    event.keyCode >= 109 && event.keyCode <= 111 ||
    event.keyCode >= 186 && event.keyCode <= 192 ||
    event.keyCode >= 219 && event.keyCode <= 222 ||
    event.keyCode == 252;
    
  if ((event.charCode || event.keyCode) &&
      ((alphNumKey && (event.ctrlKey || event.altKey || event.metaKey) &&
        !event.shiftKey &&
        // Some browsers signal AltGR as both CTRL and ALT. Do not try to
        // interpret this sequence ourselves, as some keyboard layouts use
        // it for second-level layouts.
        !(event.ctrlKey && event.altKey)) ||
       catchModifiersEarly && normalKey && !alphNumKey &&
       (event.ctrlKey || event.altKey || event.metaKey) ||
       !normalKey)) {
    lastKeyDownEvent       = event;
    var fake                    = [ ];
    fake.ctrlKey                = event.ctrlKey;
    fake.shiftKey               = event.shiftKey;
    fake.altKey                 = event.altKey;
    fake.metaKey                = event.metaKey;
    if (asciiKey) {
      fake.charCode             = event.keyCode;
      fake.keyCode              = 0;
    } else {
      fake.charCode             = 0;
      fake.keyCode              = event.keyCode;
      if (!alphNumKey && event.shiftKey) {
        fake                    = fixEvent(fake);
      }
    }

    handleKey(fake);
    lastNormalKeyDownEvent = undefined;
    
    event.stopPropagation();
    event.preventDefault();
    
    return false;
  }
  return true;
}

function init_term () {
  //$('#term_input').keypress(function (event) { keyme(event, false, true); });
  //$('#term_input').keyup(function (event) { keyme(event, true, true); });
  //$('#term_input').keydown(function (event) { keyme(event, true, false); });
  
  $('#term_input').keypress(function (e) { return vt100_keyPress(e); });
  $('#term_input').keyup(function (e) { return vt100_keyUp(e); });
  $('#term_input').keydown(function (e) { return vt100_keyDown(e); });
  
  $('#term_input').focus(function (event) {
    $('#cursor').removeClass('outline');
  });
  $('#term_input').blur(function (event) {
    $('#cursor').addClass('outline');
  });
  
  $('#term_input').dblclick(function (event) { select_mode(); });
  $('#terminal').dblclick(function (event) { select_mode(); });
  
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
    html = html + '<div id="line' + i + '"><span>&nbsp;</span></div>\n'
  }
  $("#terminal").html(html);
}

var char_w;
var char_h;

function calc_term_size () {
  var page_w = $('#term_input').outerWidth() - 4;
  var page_h = $('#term_input').outerHeight() - 4;
  
  char_w = $('#terminal_calc span').outerWidth();
  char_h = $('#terminal_calc div').outerHeight();
  
  COLS = Math.floor(page_w / char_w);
  LINES = Math.floor(page_h / char_h);
}

var pref_win;
$(document).ready(function () {
  pref_win = $("#term_pref").kendoWindow({title: 'Terminal Preferences', modal: true, width: "600px", visible: false}).data("kendoWindow");
});

function show_pref () {
  pref_win.center();
  pref_win.open();
  $("#term_pref iframe").attr('src', '/term_pref/');
}

function update_prefs (new_prefs) {
  pref_win.close();
  
  $('body').css('background-image', 'url(' + new_prefs.bg + ')');
  $('body').css('font-family', new_prefs.font);
  $('body').css('font-size', new_prefs.fontsize);
  
  $('#terminal').css('font-family', new_prefs.font);
  send_resize();
}

function send_resize () {
  var OLDC = COLS;
  var OLDL = LINES;
  
  calc_term_size();
  
  if (OLDC != COLS || OLDL != LINES) {
    if (current_ts) {
      var data = {
        action: 'resize',
        cols: COLS,
        lines: LINES,
        tsid: current_ts
      };
      resize_term();
      ws.send(JSON.stringify(data));
    }
  }
}

$(window).resize(function() {
  send_resize();
});

