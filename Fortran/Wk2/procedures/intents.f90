program intents

        implicit none
        ! intent in specifies that the argument's value will be used,
        ! but not modified. intent out specifies that the argument's
        ! value will be replaced by the function. intent inout specifices
        ! that the argument's value in the caller will be used but also
        ! modified by the function.
        integer :: m
        ! integer, parameter :: m This will cause an error.

        m = 5
        print *, m
        call increment(m)
        print *, m

contains
        
        subroutine increment(n)
                
                implicit none
                integer, intent(inout) :: n

                n = n+1
                
        end subroutine increment

        function factorial(n) result(fac)

                implicit none
                integer, value :: n 
                ! The value flag tells the compiler to use
                ! call by value semantics and the variable
                ! n can be modified just like other programming
                ! languages without modifying the passed variable.
                integer :: fac

                fac = 1

                do while (n > 1)
                        fac = fac*n
                        n = n - 1
                enddo
        end function factorial

        subroutine clamp(val, min_val, max_val)
                ! This function can be called by
                ! using the variable keywords as follows
                ! real :: value
                ! call clamp(min_val = 1.0, max_val = 5.0, val = value)


                implicit none
                real :: val, min_val, max_val

        end subroutine clamp

        integer function persistent()

                implicit none
                ! This means that subsequent function calls
                ! can use the value of new_val from the last
                ! function call. 
                real, save :: new_val        
        
        end function persistent

        subroutine optionalArgs(val, max_val, min_val)
        
                implicit none
                real, intent(inout) :: val
                real, value, optional :: min_val
                real, value :: max_val

                if (.not. present(min_val)) min_val = - max_val

                if (val < min_val) then
                        val = min_val
                elseif (max_val < val) then
                        val = max_val
                endif

        end subroutine optionalArgs

end program intents
