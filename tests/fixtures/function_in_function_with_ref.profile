SCRIPT  tests/test_plugin/function_in_function_with_ref.vim
Sourced 1 time
Total time:   0.000058
 Self time:   0.000031

count  total (s)   self (s)
                            " Test for dict function in function (local scope).
                            "
                            " This saves a ref to keep profiling information as a workaround for
                            " https://github.com/vim/vim/issues/2350.
                            " It causes the inner functions to appear before the outer in the output.
                            
    1              0.000006 let g:refs = []
                            
    1              0.000003 function! Outer()
                              function! GetObj()
                                let obj = {}
                                function obj.func()
                                  return 1
                                endfunction
                                return obj
                              endfunction
                            
                              let obj = GetObj()
                              call obj.func()
                            
                              let g:refs += [obj]
                            endfunction
    1   0.000033   0.000006 call Outer()

FUNCTION  1()
    Defined: tests/test_plugin/function_in_function_with_ref.vim line 12
Called 1 time
Total time:   0.000001
 Self time:   0.000001

count  total (s)   self (s)
    1              0.000001       return 1

FUNCTION  GetObj()
    Defined: tests/test_plugin/function_in_function_with_ref.vim line 10
Called 1 time
Total time:   0.000008
 Self time:   0.000008

count  total (s)   self (s)
    1              0.000002     let obj = {}
    1              0.000001     function obj.func()
                                  return 1
                                endfunction
    1              0.000002     return obj

FUNCTION  Outer()
    Defined: tests/test_plugin/function_in_function_with_ref.vim line 9
Called 1 time
Total time:   0.000028
 Self time:   0.000019

count  total (s)   self (s)
    1              0.000001   function! GetObj()
                                let obj = {}
                                function obj.func()
                                  return 1
                                endfunction
                                return obj
                              endfunction
                            
    1   0.000014   0.000006   let obj = GetObj()
    1   0.000003   0.000002   call obj.func()
                            
    1              0.000002   let g:refs += [obj]

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000028   0.000019  Outer()
    1   0.000008             GetObj()
    1   0.000001             1()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1   0.000028   0.000019  Outer()
    1              0.000008  GetObj()
    1              0.000001  1()

