program greatest_common_divisor
        implicit none
        
        integer, parameter :: val1 = 728, val2 = 900
        print *, gcd(val1, val2)

contains
        
        integer function gcd(a, b)
                implicit none
                integer, value :: a, b
                do while (a /=b)
                        if (a > b) then
                                a = a-b
                        else if (b > a) then
                                b = b-a
                        endif
                enddo
           gcd = a     
        end function gcd
end program greatest_common_divisor
