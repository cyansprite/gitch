" Keymap
let s:keymap = []
let s:keymap += [['Help','?','Toggle quick help']]
let s:keymap += [['Close','q','Close']]
let s:keymap += [['Enter','<cr>','Open']]
let s:keymap += [['Status','s','Status']]

let s:gitch = {}
let s:index = 1
let s:gitchList = []

function! s:gitch.BindKey()
    let map_options =' <nowait> <silent> <buffer> '
    for i in s:keymap
        silent exec 'nmap '.map_options.i[1].' <plug>gitch'.i[0]
        silent exec 'nnoremap '.map_options.'<plug>gitch'.i[0]
            \ .' :call <sid>gitchAction("'.i[0].'")<cr>'
    endfor
"    if exists('*g:gitch_CustomMap')
"        call g:gitch_CustomMap()
"    endif
endfunction

function! s:gitch.Init()
    let self.bufname = "gitch"
    " let self.opendiff = g:gitch_DiffAutoOpen
    let self.showHelp = 0
    call append(0,'')
    call append(0,'" Press ? for help.')
    let s:index = s:index + 2
endfunction

function! s:gitch.Show()
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

    call self.BindKey()
endfunction

function! s:gitch.Action(action)
    exec 'call self.Action'.a:action.'()'
endfunction

function! s:gitch.ActionHelp()
    setlocal modifiable
    let self.showHelp = !self.showHelp
    if self.showHelp
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

function! s:gitch.ActionEnter()
    if line('.') - s:index < 0
        return
    endif

    if getline('.') == s:gitchList[line('.') - s:index]
        exec 'cd '. s:gitchList[line('.') - s:index]
        exec 'e .'
    else
        throw 'You fucked up somehow'
    endif
endfunction

function! s:gitch.ActionStatus()
    if line('.') - s:index < 0
        return
    endif

    if getline('.') == s:gitchList[line('.') - s:index]
        call GitStatus(s:gitchList[line('.') - s:index])
    else
        throw 'You fucked up somehow'
    endif
endfunction

function! s:gitch.ActionClose()
    echom "quit"
endfunction

function! s:gitchAction(action)
    call s:gitch.Action(a:action)
endfunction

function! gitch#gitchShow()
    call s:gitch.Init()
    call s:gitch.Show()
    call gitch#gitList(s:gitchList)
endfunction

function! gitch#gitList(list)
    let s:gitchList = deepcopy(a:list)

    if &filetype != 'gitch'
        return
    endif

    setlocal modifiable
    silent exec s:index.',$ d _'
    call append(s:index - 1, s:gitchList)
    setlocal nomodifiable
endfunc
