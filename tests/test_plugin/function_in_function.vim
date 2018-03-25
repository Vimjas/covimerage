" Test for dict function in function.

function! GetObj()
  let obj = {}
  function obj.func()
    return 1
  endfunction
  return obj
endfunction

let obj = GetObj()
call obj.func()
