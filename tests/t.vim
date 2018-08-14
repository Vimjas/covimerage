let prof_fname = get(g:, 'prof_fname')
exe 'profile start '.prof_fname
profile! file tests/test_plugin/**

let sfile = expand('<sfile>')
let &runtimepath = $PWD.'/tests/test_plugin,'.&runtimepath

" call test_plugin#func1(1)

" autocmd SourceCmd * echom 'SOURCE: '.expand('<amatch>')
" function! s:dump_anonymous_functions()
"   redir => output
"     
"   redir END
" endfunction
" autocmd VimLeave * 
"
" augroup END
