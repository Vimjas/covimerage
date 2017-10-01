" Test for detection of conditional functions.

if 0
  function Foo()
    return 1
  endfunction
else
  function Foo()
    return 1
  endfunction
endif

if Foo()
  function Bar()
    echom 1
  endfunction
else
  function Bar()
    echom 1
  endfunction
endif

call Bar()
