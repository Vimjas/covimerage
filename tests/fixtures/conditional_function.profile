SCRIPT  tests/test_plugin/conditional_function.vim
Sourced 1 time
Total time:   0.000094
 Self time:   0.000074

count  total (s)   self (s)
                            " Test for detection of conditional functions.
                            
    1              0.000007 if 0
                              function Foo()
                                return 1
                              endfunction
                            else
    1              0.000002   function Foo()
                                return 1
                              endfunction
    1              0.000001 endif
                            
    1   0.000013   0.000008 if Foo()
    1              0.000002   function Bar()
                                echom 1
                              endfunction
    1              0.000001 else
                              function Bar()
                                echom 1
                              endfunction
                            endif
                            
    1   0.000021   0.000007 call Bar()

FUNCTION  Foo()
Called 1 time
Total time:   0.000005
 Self time:   0.000005

count  total (s)   self (s)
    1              0.000003     return 1

FUNCTION  Bar()
Called 1 time
Total time:   0.000015
 Self time:   0.000015

count  total (s)   self (s)
    1              0.000014     echom 1

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000015             Bar()
    1   0.000005             Foo()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1              0.000015  Bar()
    1              0.000005  Foo()

