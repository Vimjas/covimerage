" Test for line count with inner functions.
function! Outer()
  " comment1
  function! Inner()
    " comment2
  endfunction
endfunction
call Outer()
