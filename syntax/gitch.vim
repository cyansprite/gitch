if exists("b:current_syntax")
    finish
endif

let s:sep = '\\\'
" execute 'syntax match GitchFirst /'. '.\+'.'/ contains=GitchDir'
" execute 'syntax match GitchDir /\'. s:sep . '.\+' .'/ contains=GitchSlash'
" "execute 'syntax match GitchPath /'. '\w\+'.'/'
" "execute 'syntax match GitchHelp /'. '".\+'.'/'
" "execute 'syntax match GitchSlash /\'. s:sep . '/'
" "
" "highlight default link GitchFirst   Function
" "highlight default link GitchDir     Directory
" "highlight default link GitchSlash   Title
" "highlight default link GitchHelp    Comment
" "highlight default link lololol      Comment
" "highlight default link GitchPath    Directory

let b:current_syntax = 'gitch'
