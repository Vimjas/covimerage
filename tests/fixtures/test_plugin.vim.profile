SCRIPT  /home/daniel/src/covimerage/test_plugin/autoload/test_plugin.vim
Sourced 2 times
Total time:   0.000128
 Self time:   0.000050

count  total (s)   self (s)
                            " Test parsing of dict function.
    2              0.000007 let obj = {}
    2              0.000004 function! obj.dict_function(arg) abort
                              if a:arg
                                echom a:arg
                              else
                                echom a:arg
                              endif
                            endfunction
                            
    2   0.000049   0.000013 call obj.dict_function(0)
    2   0.000026   0.000004 call obj.dict_function(1)
    2   0.000026   0.000006 call obj.dict_function(2)

FUNCTION  2()
Called 3 times
Total time:   0.000027
 Self time:   0.000027

count  total (s)   self (s)
    3              0.000002   if a:arg
    2              0.000008     echom a:arg
    2              0.000001   else
    1              0.000008     echom a:arg
    1              0.000001   endif

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    3   0.000027             2()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    3              0.000027  2()

