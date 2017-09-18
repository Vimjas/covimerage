" Generate profile output for merged profiles.
" Used merged_profiles-init.vim
if !exists('s:conditional')
  function! F()
    echom 1
  endfunction
  let s:conditional = 1
  echom 1
  call F()
  call NeomakeTestsProfileRestart()
  exe 'source ' . expand('<sfile>')
else
  function! F()
    echom 2
  endfunction
  echom 2
  call F()
endif

