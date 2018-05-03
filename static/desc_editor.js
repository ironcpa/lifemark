var editor_module = {}
editor_module.INDENT = '  '
editor_module.HEADERS = {todo: '-',
                         progress: '>',
                         complete: '+',
                         postpone: 'p',
                         cancel: 'x'}
editor_module.EDITOR = 'editor'
editor_module.BUTTONS_NAME = 'editor_buttons'
editor_module.set_editor = function(name) {
    editor_module.EDITOR = name
    get_editor().onkeydown = handle_keys

    create_editor_buttons(get_editor())
}

function create_button(title, callback_name) {
    return "<input type='button' value='"+title+"' onclick='"+callback_name+"' tabindex='-1' />"
}
function remove_buttons() {
    $('#' + editor_module.BUTTON_NAME).remove()
}
function create_editor_buttons(editor) {
    var buttons = [create_button('add', 'insert_new_line_blow()'),
                   create_button('del', 'delete_curr_line()'),
                   create_button('>', 'indent_selected()'),
                   create_button('<', 'indent_selected(-1)'),
                   create_button('[-]', 'set_header_selected(editor_module.HEADERS.todo)'),
                   create_button('[>]', 'set_header_selected(editor_module.HEADERS.progress)'),
                   create_button('[+]', 'set_header_selected(editor_module.HEADERS.complete)'),
                   create_button('[p]', 'set_header_selected(editor_module.HEADERS.postpone)'),
                   create_button('[x]', 'set_header_selected(editor_module.HEADERS.cancel)')]

    var table_str = '<table id=' + editor_module.BUTTON_NAME + '><tr>'
    for (i=0; i<buttons.length; i++) {
        table_str += '<td>' + buttons[i] + '</td>'
    }
    table_str += '</tr></table>'

    remove_buttons()
    $('#' + editor_module.EDITOR).before(table_str)
}
function get_editor() {
    // return $('#editor')[0]
    return $('#' + editor_module.EDITOR)[0]
}
function handle_keys(e) {
    var info = e + '\n' + e.ctrlKey + '\n' + e.keyCode
    // console.log('handle_key: ' + info)

    if (e.ctrlKey && e.keyCode == 189) {
        e.preventDefault()
        set_header_selected(editor_module.HEADERS.todo)
    } else if (e.ctrlKey && e.keyCode == 187) {
        e.preventDefault()
        set_header_selected(editor_module.HEADERS.complete)
    } else if (e.ctrlKey && e.keyCode == 79) {
        e.preventDefault()
        set_header_selected(editor_module.HEADERS.progress)
    } else if (e.ctrlKey && e.keyCode == 80) {
        e.preventDefault()
        set_header_selected(editor_module.HEADERS.postpone)
    } else if (e.ctrlKey && e.keyCode == 88) {
        e.preventDefault()
        set_header_selected(editor_module.HEADERS.cancel)
    } else if (e.ctrlKey && e.keyCode == 190) {
        e.preventDefault()
        indent_selected()
    } else if (e.ctrlKey && e.keyCode == 188) {
        e.preventDefault()
        indent_selected(-1)
    } else if (e.ctrlKey && e.keyCode == 13) {
        e.preventDefault()
        insert_new_line_blow()
    } else if (e.ctrlKey && e.keyCode == 68) {
        e.preventDefault()
        // delete_curr_line()
        delete_selected_lines()
    }
}
function get_curr_line() {
    var editor = get_editor()
    var pos = editor.selectionStart
    var content = editor.value

    var lines = content.split('\n')

    var cur_len = 0
    for (i=0; i<lines.length; i++) {
        var line = lines[i]

        cur_len += line.length + 1
        if (cur_len > pos) {
            return {line:i, text:line, pos:pos}
        }
    }
    return {line:0, text:undefined, pos:0}
}
function get_line(line_no) {
    var editor = get_editor()
    var pos = editor.selectionStart
    var content = editor.value

    var lines = content.split('\n')

    return {line: line_no, text: lines[line_no], pos}
}
function set_editor_focus(pos_start, pos_end) {
    pos_end = pos_end || pos_start

    var editor = get_editor()
    var old_scroll_pos = editor.scrollTop

    editor.focus()
    editor.selectionStart = pos_start
    editor.selectionEnd = pos_end

    editor.scrollTop = old_scroll_pos
}
function replace_line(line_no, new_line) {
    var editor = get_editor()

    var lines = editor.value.split('\n')
    lines[line_no] = new_line

    return lines.join('\n')
}
function get_selected_line_nos() {
    var editor = get_editor()
    var sel_start = editor.selectionStart
    var sel_end = editor.selectionEnd

    var lines = editor.value.split('\n')
    var line_nos = []
    var cur_pos = 0
    for (i=0; i<lines.length; i++) {
        var lstart = cur_pos
        var lend = cur_pos + lines[i].length
        if (   (lstart <= sel_start && sel_start <= lend)
            || (lstart >= sel_start && lend <= sel_end)
            || (lstart <= sel_end && sel_end <= lend)) {
            line_nos.push(i)
        }
        cur_pos += lines[i].length + 1
    }
    console.log('get_selected_line_nos: ' + line_nos)
    return line_nos
}
function indent_line(line_no, indent) {
    indent = indent || 1

    var l = get_line(line_no)
    var old_pos = l.pos
    var content = l.text
    var delta = Math.abs(indent)
    if (indent > 0) {
        content = editor_module.INDENT.repeat(delta) + content
    } else {
        if (content.startsWith(editor_module.INDENT)) {
            content = content.substring(delta * editor_module.INDENT.length)
        }
    }

    var new_value = replace_line(line_no, content)
    get_editor().value = new_value
}
function indent_selected(indent) {
    indent = indent || 1

    var editor = get_editor()
    var old_sel_start = editor.selectionStart
    var old_sel_end = editor.selectionEnd

    var lines = get_selected_line_nos()
    for (i=0; i<lines.length; i++) {
        indent_line(lines[i], indent)
    }

    var d = indent * editor_module.INDENT.length

    var new_sel_start = old_sel_start + d
    var new_sel_end = old_sel_end + lines.length * d
    set_editor_focus(new_sel_start, new_sel_end)
}
function set_header_selected(header) {
    var lines = get_selected_line_nos()
    for (var i=0; i<lines.length; i++) {
        set_header(lines[i], header)
    }
}
function insert_new_line_blow() {
    var line_data = get_curr_line()
    var line_no = line_data.line
    var old_pos = line_data.pos

    var editor = get_editor()
    var lines = editor.value.split('\n')

    lines.splice(line_no + 1, 0, '')
    var content = lines.join('\n')

    var new_pos = 0
    for (i=0; i<lines.length; i++) {
        if (i > line_no)
            break

        new_pos += lines[i].length + 1  // line + \n length
    }

    editor.value = content
    set_editor_focus(new_pos)
}
function delete_selected_lines() {
    var line_nos = get_selected_line_nos()
    var old_pos = get_curr_line().pos

    var editor = get_editor()
    var lines = editor.value.split('\n')

    var start_lno = line_nos[0]
    var del_len = line_nos.length
    for (var i=0; i<del_len; i++) {
        lines.splice(start_lno, 1)
    }
    var content = lines.join('\n')

    editor.value = content
    set_editor_focus(old_pos)
}
function delete_curr_line() {
    var line_data = get_curr_line()
    var line_no = line_data.line
    var old_pos = line_data.pos

    var editor = get_editor()
    var lines = editor.value.split('\n')

    lines.splice(line_no, 1)
    content = lines.join('\n')

    editor.value = content
    set_editor_focus(old_pos)
}
function delete_line(line_no) {
    var editor = get_editor()
    var lines = editor.value.split('\n')

    lines.splice(line_no, 1)
    content = lines.join('\n')

    editor.value = content
    console.log('delete_line: ' + line_no + ' =======')
    console.log(content)
}
function set_header(line_no, header) {
    var l = get_line(line_no)
    var old_pos = l.pos
    var new_pos = 0
    var content = l.text

    var has_header = false

    var indent = 0
    var indent_str = ''
    for (i=0; i<content.length; i++) {
        if (content[i] == ' ') {
            indent++
            indent_str += ' '
        } else {
            break
        }
    }
    content = content.substring(indent)

    if (content.length >= 2 && content[1] == ' ') {
        var curr_header = content.substring(0, 2)
        for (k in editor_module.HEADERS) {
            if (curr_header == editor_module.HEADERS[k] + ' ') {
                has_header = true
                break
            }
        }
    }

    if (has_header) {
        content = content.substring(2)
        new_pos = old_pos
    }
    else {
        new_pos = old_pos + editor_module.INDENT.length
    }

    content = indent_str + header + ' ' + content
    get_editor().value = replace_line(line_no, content)

    set_editor_focus(new_pos)
}
