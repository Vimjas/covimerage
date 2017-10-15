let s:profile_count = 0
function! NeomakeTestsProfileRestart()
  let s:profile_count += 1
  if s:profile_count > 1
    echom 'stop'
    profile stop
  endif
  let profile_file = printf('tests/fixtures/merge-%d.profile', s:profile_count)
  exec 'profile start '.profile_file
  exe 'profile! file ./*.vim'
endfunction

call NeomakeTestsProfileRestart()

source test_plugin/merged_profiles.vim
