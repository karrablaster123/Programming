program multidim

        implicit none
        integer, parameter :: ROWS = 3, COLS = 5
        real, dimension(ROWS, COLS) :: A
        integer :: i, j
        real, dimension(5, 5) :: B = 1
        real :: total, rslt
       

        

        A = reshape([ (((i-1)*size(A, 2) + j, j=1, size(A, 2)), i=1, size(A, 1)) ], shape(A))
        do i = 1, size(A, 1)
                print *, A(i, :)
        enddo
        total = 0.0
        do j = 1, size(A, 2)
                do i = 1, size(A, 1)
                        total = total + A(i, j)**2
                enddo
        enddo
        
        print '(/, A, F10.2)', 'total = ', total
        
        !rslt = trace(A) Will trigger error

        print *, trace(B)

contains
        real function trace(matrix)

                use, intrinsic :: iso_fortran_env
                implicit none

                real, dimension(:, :), intent(in) :: matrix
                integer :: i

                if(size(matrix, 1) /= size(matrix, 2)) then
                        write (unit=error_unit, fmt='(A)') 'error: cannot compute the trace of a non-square matrix'
                        stop 1
                endif

                trace = 0.0

                do i = 1, size(matrix, 1)
                        trace = trace + matrix(i, i)
                enddo
        end function trace

        function eye(n) result(matrix)

                implicit none
                integer, value :: n
                real, dimension(n, n) :: matrix
                integer :: i

                matrix = 0.0
                do i = 1, size(matrix, 1)
                        matrix(i, i) = 1.0
                enddo
        
        end function eye
end program multidim
