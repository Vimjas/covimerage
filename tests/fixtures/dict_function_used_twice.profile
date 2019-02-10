SCRIPT  tests/test_plugin/dict_function_used_twice.vim
Sourced 1 time
Total time:   0.000174
 Self time:   0.000088

count  total (s)   self (s)
                            " Test parsing of dict function that gets used twice.
    1              0.000015 let base = {}
    1              0.000006 function! base.base_function() abort dict
                              if 1
                                echom 1
                              else
                                echom 2
                              endif
                            endfunction
                            
    1              0.000009 let obj1 = deepcopy(base)
    1              0.000003 function! obj1.func() abort
                              call self.base_function()
                            endfunction
                            
    1              0.000004 let obj2 = deepcopy(base)
    1              0.000001 function! obj2.func() abort
                              call self.base_function()
                            endfunction
                            
    1   0.000034   0.000007 call obj1.func()
    1   0.000039   0.000006 call obj2.func()
    1   0.000019   0.000006 call obj1.base_function()
    1   0.000019   0.000007 call obj2.base_function()

FUNCTION  1()
Called 4 times
Total time:   0.000070
 Self time:   0.000070

count  total (s)   self (s)
    4              0.000007   if 1
    4              0.000042     echom 1
    4              0.000006   else
                                echom 2
                              endif

FUNCTION  2()
Called 1 time
Total time:   0.000028
 Self time:   0.000009

count  total (s)   self (s)
    1   0.000026   0.000008   call self.base_function()

FUNCTION  3()
Called 1 time
Total time:   0.000033
 Self time:   0.000007

count  total (s)   self (s)
    1   0.000032   0.000007   call self.base_function()

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    4   0.000070             1()
    1   0.000033   0.000007  3()
    1   0.000028   0.000009  2()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    4              0.000070  1()
    1   0.000028   0.000009  2()
    1   0.000033   0.000007  3()

