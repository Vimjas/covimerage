SCRIPT  /test_plugin/conditional_function.vim
Sourced 1 time
Total time:   0.000239
 Self time:   0.000234

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
    1              0.000002 endif
                            
    1   0.000014   0.000009 if Foo()
    1              0.000003   function Bar()
                                echom 1
                              endfunction
    1              0.000001 else
                              function Bar()
                                echom 1
                              endfunction
                            endif
                            
    1              0.000170 Bar()

FUNCTION  Foo()
Called 1 time
Total time:   0.000005
 Self time:   0.000005

count  total (s)   self (s)
    1              0.000003     return 1

FUNCTION  Bar()
Called 0 times
Total time:   0.000000
 Self time:   0.000000

count  total (s)   self (s)
                                echom 1

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000005             Foo()
                             Bar()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1              0.000005  Foo()
                             Bar()

