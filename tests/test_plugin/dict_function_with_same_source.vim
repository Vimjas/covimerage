" Test parsing of dict function (with same source).
let obj1 = {}
function! obj1.dict_function(arg) abort
  if a:arg
    echom a:arg
  else
    echom a:arg
  endif
endfunction

let obj2 = {}
function! obj2.dict_function(arg) abort
  if a:arg
    echom a:arg
  else
    echom a:arg
  endif
endfunction

call obj2.dict_function(0)
call obj2.dict_function(1)
call obj2.dict_function(2)
call obj1.dict_function(3)
