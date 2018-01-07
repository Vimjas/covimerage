SCRIPT  tests/test_plugin/function_in_function_count.vim
Sourced 1 time
Total time:   0.000056
 Self time:   0.000037

count  total (s)   self (s)
                            " Test for line count with inner functions.
    1              0.000007 function! Outer()
                              " comment1
                              function! Inner()
                                " comment2
                              endfunction
                            endfunction
    1   0.000032   0.000012 call Outer()

FUNCTION  Inner()
Called 0 times
Total time:   0.000000
 Self time:   0.000000

count  total (s)   self (s)
                                " comment2

FUNCTION  Outer()
Called 1 time
Total time:   0.000019
 Self time:   0.000019

count  total (s)   self (s)
                              " comment1
    1              0.000002   function! Inner()
                                " comment2
                              endfunction

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000019             Outer()
                             Inner()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1              0.000019  Outer()
                             Inner()

