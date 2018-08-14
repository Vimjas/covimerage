" https://github.com/vim/vim/issues/3286
function! s:function(name) abort
  echom a:name
endfunction

call s:function('name')
call test_plugin#function#function('name')
