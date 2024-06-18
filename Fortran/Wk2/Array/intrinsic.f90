program intrin

        implicit none
        real, dimension(2, 2) :: A = 1, B = 2
        real, dimension(1, 4) :: C
        
        C = reshape(A, [1, 4])
        A = reshape(C, [2, 2])
        print *, rank(A)
        print *, sin(A)
        print *, "Max val: ", maxval(A) !minval
        print *, "Max loc: ", maxloc(A) !minloc
        ! dim = 1 sum all the rows
        ! Can also use masks to select parts of array
        ! dim = 2 sum all the columns
        print *, sum(B, dim = 1)


end program intrin
