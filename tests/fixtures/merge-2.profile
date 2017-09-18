SCRIPT  /test_plugin/merged_profiles.vim
Sourced 1 time
Total time: 76887.125215
 Self time: 76887.125183

count  total (s)   self (s)
                            " Generate profile output for merged profiles.
                            " Used merged_profiles-init.vim
    1              0.000009 if !exists('s:conditional')
                              function! F()
                                echom 1
                              endfunction
                              let s:conditional = 1
                              echom 1
                              call F()
                              call NeomakeTestsProfileRestart()
                              exe 'source ' . expand('<sfile>')
    1              0.000001 else
    1              0.000002   function! F()
                                echom 2
                              endfunction
    1              0.000024   echom 2
    1   0.000030   0.000014   call F()
    1              0.000002 endif
                            

FUNCTION  F()
Called 1 time
Total time:   0.000016
 Self time:   0.000016

count  total (s)   self (s)
    1              0.000011     echom 2

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000016             F()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1              0.000016  F()

