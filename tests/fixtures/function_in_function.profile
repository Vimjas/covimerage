SCRIPT  tests/test_plugin/function_in_function.vim
Sourced 1 time
Total time:   0.000239
 Self time:   0.000156

count  total (s)   self (s)
                            " Test for dict function in function.
                            
    1              0.000021 function! GetObj()
                              let obj = {}
                              function obj.func()
                                return 1
                              endfunction
                              return obj
                            endfunction
                            
    1   0.000115   0.000040 let obj = GetObj()
    1   0.000032   0.000023 call obj.func()

FUNCTION  GetObj()
Called 1 time
Total time:   0.000075
 Self time:   0.000075

count  total (s)   self (s)
    1              0.000026   let obj = {}
    1              0.000011   function obj.func()
                                return 1
                              endfunction
    1              0.000009   return obj

FUNCTION  1()
Called 1 time
Total time:   0.000008
 Self time:   0.000008

count  total (s)   self (s)
    1              0.000006     return 1

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000075             GetObj()
    1   0.000008             1()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1              0.000075  GetObj()
    1              0.000008  1()

