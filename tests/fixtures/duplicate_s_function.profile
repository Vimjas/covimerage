SCRIPT  tests/test_plugin/duplicate_s_function.vim
Sourced 1 time
Total time:   0.000180
 Self time:   0.000083

count  total (s)   self (s)
                            " https://github.com/vim/vim/issues/3286
    1              0.000008 function! s:function(name) abort
                              echom a:name
                            endfunction
                            
    1   0.000032   0.000013 call s:function('name')
    1   0.000131   0.000053 call test_plugin#function#function('name')

SCRIPT  tests/test_plugin/autoload/test_plugin/function.vim
Sourced 1 time
Total time:   0.000025
 Self time:   0.000025

count  total (s)   self (s)
    1              0.000004 function! s:function(name) abort
                              echom a:name
                            endfunction
                            
    1              0.000002 function! test_plugin#function#function(name) abort
                              call s:function(a:name)
                            endfunction

FUNCTION  test_plugin#function#function()
    Defined: tests/test_plugin/autoload/test_plugin/function.vim line 5
Called 1 time
Total time:   0.000032
 Self time:   0.000007

count  total (s)   self (s)
    1   0.000031   0.000006   call s:function(a:name)

FUNCTION  <SNR>2_function()
    Defined: tests/test_plugin/duplicate_s_function.vim line 2
Called 1 time
Total time:   0.000019
 Self time:   0.000019

count  total (s)   self (s)
    1              0.000019   echom a:name

FUNCTION  <SNR>3_function()
    Defined: tests/test_plugin/autoload/test_plugin/function.vim line 1
Called 1 time
Total time:   0.000025
 Self time:   0.000025

count  total (s)   self (s)
    1              0.000024   echom a:name

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000032   0.000007  test_plugin#function#function()
    1   0.000025             <SNR>3_function()
    1   0.000019             <SNR>2_function()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1              0.000025  <SNR>3_function()
    1              0.000019  <SNR>2_function()
    1   0.000032   0.000007  test_plugin#function#function()

