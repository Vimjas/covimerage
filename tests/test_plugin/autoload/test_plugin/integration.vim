" Used for integration tests (tests/integration.sh / make test_integration).
let foo = 1
let bar = foo

function! test_plugin#integration#func1() abort
  echom 'func1'
endfunction

function! test_plugin#integration#func2() abort
  echom 'func2.1'

  echom 'func2.2'
endfunction

if foo == 2
  echom 'not covered'
endif

