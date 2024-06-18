program subroutines
        implicit none
        real :: inp = 100.5
        
        call clamp(inp, 10.0, 90.0)
        print *, inp

 contains
         subroutine clamp(val, min_val, max_val)
                implicit none
                real :: val
                real :: min_val, max_val

                if (val < min_val) then
                        val = min_val
                elseif (max_val < val) then
                        val = max_val
                endif       
         end subroutine clamp
        
end program subroutines
