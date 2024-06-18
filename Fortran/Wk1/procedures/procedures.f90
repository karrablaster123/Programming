program leap_year
        implicit none
        
        integer :: year
        logical :: has_error

        year = 1899
        print *, year, is_leap_year(year)
        print *, 'year is now', year
        print *, 1448, is_leap_year(1448, has_error = has_error)
        if (has_error) &
                print *, 'oopsie'
        
contains
        
        function is_leap_year(year, has_error) result(is_leap)
                implicit none
                integer, intent(in) :: year ! Prevents function from reassigning value.
                logical, optional, intent(out) :: has_error ! Optional parameter that is modified in function.
                ! The passed argument value will not be used (intent(out)).
                ! intent(inout) is the third option
                logical :: is_leap

                if (present(has_error)) then
                        has_error = year <= 1582
                endif

                if (mod(year, 4) == 0) then
                        if (mod(year, 100) == 0) then
                                if (mod(year, 400) == 0) then
                                        is_leap = .true.
                                else
                                        is_leap = .false.
                                end if
                        else
                                is_leap = .true.
                        end if
                else
                        is_leap = .false.
                endif
        end function is_leap_year
        

end program leap_year

