SCRIPT  /test_plugin/conditional_function.vim
Sourced 1 time
Total time:   0.000080
 Self time:   0.000063

count  total (s)   self (s)
                            " Test for detection of conditional functions.
                            
    1              0.000007 if 0
                              function Foo()
                                return 1
                              endfunction
                            else
    1              0.000003   function Foo()
                                return 1
                              endfunction
    1              0.000001 endif
                            
    1   0.000012   0.000007 if Foo()
    1              0.000002   function Bar()
                                echom 1
                              endfunction
    1              0.000001 else
                              function Bar()
                                echom 1
                              endfunction
                            endif
                            
    1   0.000021   0.000008 call Bar()

FUNCTION  Foo()
Called 1 time
Total time:   0.000004
 Self time:   0.000004

count  total (s)   self (s)
    1              0.000002     return 1

FUNCTION  Bar()
Called 1 time
Total time:   0.000013
 Self time:   0.000013

count  total (s)   self (s)
    1              0.000012     echom 1

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000013             Bar()
    1   0.000004             Foo()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1              0.000013  Bar()
    1              0.000004  Foo()

