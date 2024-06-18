program array_elements

        implicit none
        integer, dimension(5) :: A, B, C
        integer :: i
        real, dimension(5) :: AA = [ 1.2, 2.3, 3.4, 4.5, 5.6 ], &
                BB = [ -1.0, -0.5, 0.0, 0.5, 1.0 ], &
                CC
        integer, dimension(10) :: AAA = [ (i, i = 1, 10) ] 
        character(len=10), parameter :: FMT = '(10I3)'
        

        A(1) = 1

        do i = 2, size(A)
                A(i) = 2*A(i-1)
        enddo
        print *, A

        A = 13
        B = [ 2, 3, 5, 7, 11 ]
        C = [ (2**i, i=0, 4) ]
        print *, A
        print *, B
        print *, C

        CC = AA + 2.0*BB
        print *, CC

        print FMT, AAA
        print FMT, AAA(4:7)
        print FMT, AAA(:7)
        print FMT, AAA(4:)
        print FMT, AAA(4:7:2)
        print FMT, AAA(4::2)
        print FMT, AAA(:7:2)
        print FMT, AAA(7:4:-1)


end program array_elements
