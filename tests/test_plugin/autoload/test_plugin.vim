" Comment
" Another comment
let foo = 1
let bar = foo

function! test_plugin#func1(a) abort
  echom 'func1'
endfunction

function! test_plugin#func2(a) abort
  echom 'func2.1'

  echom 'func2.2'
endfunction

if foo == 2
  echom 'not covered'
endif

