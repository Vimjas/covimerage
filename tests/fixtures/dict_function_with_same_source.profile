SCRIPT  tests/test_plugin/dict_function_with_same_source.vim
Sourced 1 time
Total time:   0.000153
 Self time:   0.000080

count  total (s)   self (s)
                            " Test parsing of dict function (with same source).
    1              0.000015 let obj1 = {}
    1              0.000007 function! obj1.dict_function(arg) abort
                              if a:arg
                                echom a:arg
                              else
                                echom a:arg
                              endif
                            endfunction
                            
    1              0.000002 let obj2 = {}
    1              0.000002 function! obj2.dict_function(arg) abort
                              if a:arg
                                echom a:arg
                              else
                                echom a:arg
                              endif
                            endfunction
                            
    1   0.000032   0.000009 call obj2.dict_function(0)
    1   0.000027   0.000005 call obj2.dict_function(1)
    1   0.000021   0.000007 call obj2.dict_function(2)
    1   0.000023   0.000008 call obj1.dict_function(3)

FUNCTION  1()
Called 1 time
Total time:   0.000014
 Self time:   0.000014

count  total (s)   self (s)
    1              0.000002   if a:arg
    1              0.000008     echom a:arg
    1              0.000001   else
                                echom a:arg
                              endif

FUNCTION  2()
Called 3 times
Total time:   0.000058
 Self time:   0.000058

count  total (s)   self (s)
    3              0.000006   if a:arg
    2              0.000021     echom a:arg
    2              0.000003   else
    1              0.000014     echom a:arg
    1              0.000001   endif

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    3   0.000058             2()
    1   0.000014             1()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    3              0.000058  2()
    1              0.000014  1()

