program Numericals

        !This program deals with the numerical intricacies of fortran
        use, intrinsic :: iso_fortran_env
        use, intrinsic :: iso_fortran_env, SP => REAL32, DP => REAL64, i32 => INT32, i64 => INT64, i8 => INT8, i16 => INT16
        implicit none

        !Overflow 
        integer(kind=i8) :: val
        integer(kind=i16) :: bit16
        integer(kind=i32) :: bit32
        integer(kind=i64) :: bit64
        integer :: i

        real(SP) :: x
        real(DP) :: y

        complex(DP) :: z1, z2
        real(DP) :: re, im

        integer(i32) :: i_i32
        integer(i64) :: i_i64        

        val = 125
        
        do i = 1, 6
                print *, val
                val = val + 1
        end do

        !Sizes of integers
        print *, "INTEGER MAXIMUMS"
        print *, huge(val)
        print *, huge(bit16)
        print *, huge(bit32)
        print *, huge(bit64)
        
        ! Are these two NOT equal? (Ans = True {T}) 
        print *, 10 /= 100 

        ! Real Numbers

        !Denote type of real value with suffix
        x = 0.0_sp
        y = -1.5e-3_dp

        print *, "Real Numbers:"
        print *, x
        print *, y
        print *, "REAL DETAILS:"
        print *, "Huge: "
        print *, huge(x)
        print *, huge(y)
        print *, "Tiny: "
        print *, tiny(x)
        print *, tiny(y)
        print *, "Epsilon: "
        print *, epsilon(x)
        print *, epsilon(y)

        ! Complex Numbers
        re = -0.622772_dp
        im = 0.42193_dp

        z1 = (-0.622772_dp, 0.42193_dp)
        z2 = cmplx(re, im, DP)
        print *, "Complex Numbers"
        print *, z1
        print *, z2

        ! Type Casting
        print *, "Type Casting:"
        
        i_i64 = 2**40
        i_i32 = int(i_i64, i64)
        print *, i_i32

        print *, "Proper Type Casting:"
        i_i32 = 2**10
        i_i64 = int(i_i32, i64)
        print *, i_i64

        print *, "Real Number Casting:"
        y = 1.0e100_dp
        x = real(y, sp)
        print *, x

        im = 9.84379475_dp
        print *, "Real to Int Casting:"
        i_i64 = aint(im, i64)
        print *, i_i64

        ! One can also use real(int, kind) to convert an int to a real value or
        ! to obtain the real part of a complex number. Using aimag(cmplx, kind)
        ! returns the imaginary part of a complex number as a real number and 
        ! cmplx(val1, val2, kind) turns two numbers into a complex with (real: val1, imaginary: val2)
end program Numericals
