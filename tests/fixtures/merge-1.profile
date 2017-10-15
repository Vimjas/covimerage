SCRIPT  /test_plugin/merged_profiles.vim
Sourced 1 time
Total time:   0.000000
 Self time:   0.000000

count  total (s)   self (s)
                            " Generate profile output for merged profiles.
                            " Used merged_profiles-init.vim
    1              0.000005 if !exists('s:conditional')
    1              0.000002   function! F()
                                echom 1
                              endfunction
    1              0.000003   let s:conditional = 1
    1              0.000020   echom 1
    1   0.000020   0.000006   call F()
                              call NeomakeTestsProfileRestart()

FUNCTION  F()
Called 1 time
Total time:   0.000014
 Self time:   0.000014

count  total (s)   self (s)
    1              0.000013     echom 1

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000014             F()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1              0.000014  F()

