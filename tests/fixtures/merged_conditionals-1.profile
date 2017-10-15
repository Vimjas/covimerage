SCRIPT  tests/test_plugin/merged_conditionals.vim
Sourced 1 time
Total time:   0.000113
 Self time:   0.000091

count  total (s)   self (s)
                            " Generate profile output for merged profiles.
    1              0.000029 let cond = get(g:, 'test_conditional', 0)
                            
    1              0.000006 if cond == 1
    1              0.000004   let foo = 1
    1              0.000002 elseif cond == 2
                              let foo = 2
                            elseif cond == 3
                              let foo = 3
                            else
                              let foo = 'else'
                            endif
                            
    1              0.000005 function F(...)
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
                            
    1   0.000035   0.000013 call F(cond)

FUNCTION  F()
Called 1 time
Total time:   0.000022
 Self time:   0.000022

count  total (s)   self (s)
    1              0.000005   if a:1 == 1
    1              0.000004     let foo = 1
    1              0.000002   elseif a:1 == 2
                                let foo = 2
                              elseif a:1 == 3
                                let foo = 3
                              else
                                let foo = 'else'
                              endif

FUNCTIONS SORTED ON TOTAL TIME
count  total (s)   self (s)  function
    1   0.000022             F()

FUNCTIONS SORTED ON SELF TIME
count  total (s)   self (s)  function
    1              0.000022  F()

