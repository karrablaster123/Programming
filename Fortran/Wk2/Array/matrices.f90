program matrices

        implicit none
        integer :: i, j
        real, dimension(2, 3) :: matrix1
        real, dimension(3, 2) :: matrix2
        real, dimension(2, 2) :: matrix3

        matrix1 = reshape([2.0, 3.0, 5.0, 7.0, 11.0, 13.0], shape(matrix1))
        do i = 1, size(matrix1, 1)
                print *, matrix1(i, :)
        enddo

        matrix2 = reshape([ ((i - 2*j, i=1, 2), j=1, 3) ], shape(matrix2))
        do i = 1, size(matrix2, 1)
                print *, matrix2(i, :)
        enddo
        print *, size(matrix2)
        print *, size(matrix2, 1), size(matrix2, 2)
        matrix3 = matmul(matrix1, matrix2)
        do i = 1, size(matrix3, 1)
                print *, matrix3(i, :)
        enddo
        ! print *, matrix1 + matrix2 This is how you add matrices
        ! However, the above example will not work (compile error)
        ! since the dimensions of matrix1 and matrix2 do not match.

end program matrices
