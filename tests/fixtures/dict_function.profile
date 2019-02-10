SCRIPT  /test_plugin/dict_function.vim
Sourced 1 time
Total time:   0.000159
 Self time:   0.000066

count  total (s)   self (s)
                            " Test parsing of dict function.
    1              0.000012 let obj = {}
    1              0.000006 function! obj.dict_function(arg) abort
                              if a:arg
                                echom a:arg
                              else
                                echom a:arg
                              endif
                            endfunction
                            
    1   0.000049   0.000012 call obj.dict_function(0)
    1   0.000042   0.000010 call obj.dict_function(1)
    1   0.000034   0.000010 call obj.dict_function(2)

FUNCTION  1()
Called 3 times
Total time:   0.000093
 Self time:   0.000093

count  total (s)   self (s)
    3              0.000014   if a:arg
    2              0.000032     echom a:arg
    2              0.000004   else
    1              0.000023     echom a:arg
    1              0.000002   endif

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    3   0.000126             1()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    3              0.000126  1()

