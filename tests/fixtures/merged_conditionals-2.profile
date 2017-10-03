SCRIPT  tests/test_plugin/merged_conditionals.vim
Sourced 1 time
Total time:   0.000098
 Self time:   0.000078

count  total (s)   self (s)
                            " Generate profile output for merged profiles.
    1              0.000017 let cond = get(g:, 'test_conditional', 0)
                            
    1              0.000003 if cond == 1
                              let foo = 1
                            elseif cond == 2
    1              0.000002   let foo = 2
    1              0.000001 elseif cond == 3
                              let foo = 3
                            else
                              let foo = 'else'
                            endif
                            
    1              0.000007 function F(...)
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
                            
    1   0.000031   0.000011 call F(cond)

FUNCTION  F()
Called 1 time
Total time:   0.000020
 Self time:   0.000020

count  total (s)   self (s)
    1              0.000003   if a:1 == 1
                                let foo = 1
                              elseif a:1 == 2
    1              0.000003     let foo = 2
    1              0.000002   elseif a:1 == 3
                                let foo = 3
                              else
                                let foo = 'else'
                              endif

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000020             F()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1              0.000020  F()

