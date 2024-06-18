program logistic_map
        
        implicit none
        real :: x, r
        integer, parameter :: N_ITER = 20
        integer :: i

        x = 0.95
        r = 3.55

        do i = 0, N_ITER
                x = r*x*(1-x)
                print *, x
        enddo


end program logistic_map
