" Globals

" Keymap
let s:keymap = []
let s:keymap += [['Help','?','Toggle quick help']]
let s:keymap += [['Close','q','Close']]
let s:keymap += [['Enter','<cr>','Open']]

let s:index = 1
let s:gitchList = []
let s:opened = {}
let s:dirs = []
let s:files = []
let s:showHelp = 0

function! s:BindKey()
    let map_options =' <nowait> <silent> <buffer> '
    for i in s:keymap
        silent exec 'nmap '.map_options.i[1].' <plug>gitch'.i[0]
        silent exec 'nnoremap '.map_options.'<plug>gitch'.i[0].' :call <sid>gitchAction("'.i[0].'")<cr>'
    endfor
endfunction

function! s:Show()
    let s:bufname = "gitch"
    let s:showHelp = 0
    call append(0,'')
    call append(0,'" Press ? for help.')
    let s:index = s:index + 2

    exec "silent keepalt"
    setlocal winfixwidth
    setlocal noswapfile
    setlocal buftype=nowrite
    setlocal bufhidden=delete
    setlocal nowrap
    setlocal foldcolumn=0
    setlocal nobuflisted
    setlocal nospell
    setlocal nonumber
    setlocal norelativenumber
    setlocal cursorline
    setlocal nomodifiable
    setlocal undolevels=-1
    " setlocal statusline=%!t:gitch.GetStatusLine()
    setfiletype gitch

    call s:BindKey()
endfunction

function! s:ActionHelp()
    setlocal modifiable
    let s:showHelp = !s:showHelp
    if s:showHelp
        " delete the help line + 1 for space
        silent exec '1,2 d _'
        call append(0,'')
        for i in s:keymap
            call append(0,'" '.i[1].' : '.i[2])
        endfor
        let s:index = s:index + len(s:keymap) - 1
    else
        " delete the keymaps length help lines + 1 for space
        silent exec '1,'.string(len(s:keymap) + 1).' d _'
        call append(0,'')
        call append(0,'" Press ? for help.')
        let s:index = s:index - len(s:keymap) + 1
    endif
    setlocal nomodifiable
endfunction

function! s:OpenDir(item, curs, i, indent)
    " FIXME seps
    let tind = a:indent - &tabstop * 2
    let p = ''

    let ds = []
    let item = ''
    let i = a:i

    " if we recursing
    if a:i == -1
        while tind > 0
            let ind = search('^\s\{'.tind.'\}\w', 'bn')
            let p = substitute(getline(ind), '^\s*', '', "") . '\' . p
            let tind -= &tabstop
        endwhile

        let item = a:curs . '\' . p . a:item
        let ds = s:globMe(item)

        if isdirectory(item) && len(ds) > 0
            if !has_key(s:opened, item)
                let s:opened[item] = getline(line('.') + 1)
            else
                let start = line('.') + 1
                let end = search(s:opened[item]) - 1
                silent exec start . ','. end .' d _'
                silent normal! k
                silent call remove(s:opened, item)
                return
            endif
        else
            return
        endif
    else
        let item = a:item
        let ds = s:globMe(a:item)
    endif

    " echom a:i . ' :: ' . item

    for x in ds
        let newline = repeat(' ', a:indent) . x
        let newitem = item . '\' . x

        call append(line('.') + i + 1 , newline)

        let i = i + 1
        " FIXME SEPS
        if has_key(s:opened, newitem)
            let i = s:OpenDir(newitem, a:curs, i, a:indent + &tabstop)
        endif
    endfor
    return i
endfunc

function! s:ActionEnter()
    if line('.') - s:index < 0
        return
    endif

    let ind = search('^\w', 'bn')
    let curs = getline(ind)
    let item = substitute(getline('.'), '^\s*', '', "")

    setlocal modifiable
    call s:OpenDir(item, curs, -1, indent('.') + &tabstop)
    setlocal nomodifiable
endfunction

function! gitch#echoOpened()
    for key in keys(s:opened)
        echom key . ' - ' . s:opened[key]
    endfor
endfunc

" function! s:ActionStatus()
"     if line('.') - s:index < 0
"         return
"     endif
"
"     if getline('.') == s:gitchList[line('.') - s:index]
"         call GitStatus(s:gitchList[line('.') - s:index])
"     else
"         throw 'You fucked up somehow'
"     endif
" endfunction

function! s:ActionClose()
    echom "quit"
endfunction

function! s:gitchAction(action)
    exec 'call s:Action'.a:action.'()'
endfunction

function! gitch#gitchShow()
    call s:Show()
    setlocal modifiable
    silent exec s:index.',$ d _'

    call append(s:index - 1, getcwd())
    let s:index = s:index + 1
    let i = 0
    for d in s:globMe('.')
        call append(s:index - 1 + i, repeat(' ', &tabstop) . d)
        let i = i + 1
    endfor

    setlocal nomodifiable
endfunc

function! s:globMe(path)
    let cur = globpath(a:path, '*', 0, 1)
    let fcur = []
    let dcur = []

    " FIXME seps
    for x in cur
        if isdirectory(x)
            call add(l:dcur, substitute(x, escape(a:path.'\', '\'), '', ''))
        else
            call add(l:fcur, substitute(x, escape(a:path.'\', '\'), '', ''))
        endif
    endfor

    return extend(dcur, fcur)
endfunc
