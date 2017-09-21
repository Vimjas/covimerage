" Test parsing of dict function that gets used twice.
let base = {}
function! base.base_function() abort dict
  if 1
    echom 1
  else
    echom 2
  endif
endfunction

let obj1 = deepcopy(base)
function! obj1.func() abort
  call self.base_function()
endfunction

let obj2 = deepcopy(base)
function! obj2.func() abort
  call self.base_function()
endfunction

call obj1.func()
call obj2.func()
call obj1.base_function()
call obj2.base_function()
