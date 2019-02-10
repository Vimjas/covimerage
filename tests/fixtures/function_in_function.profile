SCRIPT  tests/test_plugin/function_in_function.vim
Sourced 1 time
Total time:   0.000042
 Self time:   0.000030

count  total (s)   self (s)
                            " Test for dict function in function.
                            
    1              0.000004 function! GetObj()
                              let obj = {}
                              function obj.func()
                                return 1
                              endfunction
                              return obj
                            endfunction
                            
    1   0.000021   0.000011 let obj = GetObj()
    1   0.000005   0.000003 call obj.func()

FUNCTION  1()
    Defined: tests/test_plugin/function_in_function.vim line 5
Called 1 time
Total time:   0.000002
 Self time:   0.000002

count  total (s)   self (s)
    1              0.000002     return 1

FUNCTION  GetObj()
    Defined: tests/test_plugin/function_in_function.vim line 3
Called 1 time
Total time:   0.000010
 Self time:   0.000010

count  total (s)   self (s)
    1              0.000003   let obj = {}
    1              0.000001   function obj.func()
                                return 1
                              endfunction
    1              0.000002   return obj

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000010             GetObj()
    1   0.000002             1()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1              0.000010  GetObj()
    1              0.000002  1()

