SCRIPT  tests/test_plugin/dict_function_with_continued_lines.vim
Sourced 1 time
Total time:   0.000158
 Self time:   0.000078

count  total (s)   self (s)
                            " Test parsing of dict function with continued lines.
    1              0.000018 let obj = {}
    1              0.000007 function! obj.dict_function(arg) abort
                              if a:arg
                                echom
                                      \ a:arg
                                      \ .'.'
                              else
                                echom a:arg
                              endif
                            endfunction
                            
    1   0.000044   0.000013 call obj.dict_function(0)
    1   0.000040   0.000008 call obj.dict_function(1)
    1   0.000025   0.000008 call obj.dict_function(1)

FUNCTION  1()
Called 3 times
Total time:   0.000079
 Self time:   0.000079

count  total (s)   self (s)
    3              0.000008   if a:arg
    2              0.000059     echom a:arg .'.'
    2              0.000003   else
    1              0.000114     echom a:arg
    1              0.000002   endif

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    3   0.000079             1()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    3              0.000079  1()

