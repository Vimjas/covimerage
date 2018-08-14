function! s:function(name) abort
  echom a:name
endfunction

function! test_plugin#function#function(name) abort
  call s:function(a:name)
endfunction
