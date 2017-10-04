SCRIPT  tests/test_plugin/merged_conditionals.vim
Sourced 1 time
Total time:   0.000084
 Self time:   0.000070

count  total (s)   self (s)
                            " Generate profile output for merged profiles.
    1              0.000025 let cond = get(g:, 'test_conditional', 0)
                            
    1              0.000004 if cond == 1
                              let foo = 1
                            elseif cond == 2
                              let foo = 2
                            elseif cond == 3
                              let foo = 3
                            else
    1              0.000003   let foo = 'else'
    1              0.000001 endif
                            
    1              0.000003 function F(...)
                              if a:1 == 1
                                let foo = 1
                              elseif a:1 == 2
                                let foo = 2
                              elseif a:1 == 3
                                let foo = 3
                              else
                                let foo = 'else'
                              endif
                            endfunction
                            
    1   0.000024   0.000010 call F(cond)

FUNCTION  F()
Called 1 time
Total time:   0.000014
 Self time:   0.000014

count  total (s)   self (s)
    1              0.000002   if a:1 == 1
                                let foo = 1
                              elseif a:1 == 2
                                let foo = 2
                              elseif a:1 == 3
                                let foo = 3
                              else
    1              0.000002     let foo = 'else'
    1              0.000001   endif

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000014             F()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1              0.000014  F()

