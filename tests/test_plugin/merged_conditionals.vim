" Generate profile output for merged profiles.
let cond = get(g:, 'test_conditional', 0)

if cond == 1
  let foo = 1
elseif cond == 2
  let foo = 2
elseif cond == 3
  let foo = 3
else
  let foo = 'else'
endif

function F(...)
  if a:1 == 1
    let foo = 1
  elseif a:1 == 2
    let foo = 2
  elseif a:1 == 3
    let foo = 3
  else
    let foo = 'else'
  endif
endfunction

call F(cond)
