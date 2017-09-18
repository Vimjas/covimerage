SCRIPT  /test_plugin/autoload/test_plugin.vim
Sourced 1 time
Total time:   0.000033
 Self time:   0.000033

count  total (s)   self (s)
                            function! test_plugin#func1(a) abort
                              echom 'func1'
                            endfunction
                            
    1              0.000005 function! test_plugin#func2(a) abort
                              echom 'func2'
                            endfunction
                            

FUNCTION  test_plugin#func2()
Called 0 times
Total time:   0.000000
 Self time:   0.000000

count  total (s)   self (s)
                              echom 'func2'

FUNCTION  test_plugin#func1()
Called 1 time
Total time:   0.000037
 Self time:   0.000037

count  total (s)   self (s)
    1              0.000035   echom 'func1'

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000037             test_plugin#func1()
                             test_plugin#func2()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1              0.000037  test_plugin#func1()
                             test_plugin#func2()

