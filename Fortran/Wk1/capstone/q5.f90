program fibonacci
        
        implicit none
        integer, parameter :: N_ITER = 60
        integer(kind=8) :: i, temp, last = 0, current = 1

        do i=1, N_ITER
                print *, last
                temp = current
                current = current + last
                last = temp
        enddo
        
end program fibonacci

