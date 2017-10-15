" Test parsing of dict function.
let obj = {}
function! obj.dict_function(arg) abort
  if a:arg
    echom a:arg
  else
    echom a:arg
  endif
endfunction

call obj.dict_function(0)
call obj.dict_function(1)
call obj.dict_function(2)
