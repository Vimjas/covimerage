" Test for dict function in function (local scope).
"
" This saves a ref to keep profiling information as a workaround for
" https://github.com/vim/vim/issues/2350.
" It causes the inner functions to appear before the outer in the output.

let g:refs = []

function! Outer()
  function! GetObj()
    let obj = {}
    function obj.func()
      return 1
    endfunction
    return obj
  endfunction

  let obj = GetObj()
  call obj.func()

  let g:refs += [obj]
endfunction
call Outer()
