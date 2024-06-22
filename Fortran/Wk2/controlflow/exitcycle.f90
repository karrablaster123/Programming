program exitcycle

        implicit none
        
        integer :: i = 0

        ! Infinite Loop
        do
                i = i + 1
                
                if (i < 7) then
                        cycle ! This skips any code below. 
                endif

                if (i > 5) then
                        exit ! allows one to exit a loop
                endif
        enddo
        print *, "Out of the Loop!", i

contains
        function has_duplicates(data) result(result)
                integer, dimension(:), intent(in) :: data
                logical :: result
                integer :: i, j

                result = .false.
                outer: do i = 1, size(data) - 1 ! Named do loop allows one to exit nested loops.
                        do j = i + 1, size(data)
                                if (data(i) == data(j)) then
                                        result = .true.
                                        exit outer
                                end if
                        end do
                end do outer
        end function has_duplicates


end program exitcycle
