program IO
    implicit none
    integer :: i = 123456
    character(len=6) :: c = 'abcdef'
    real :: r = 1.239, r2 = 1.23e5

    print '(I8)', i
    print '(I4)', i ! Asterisks printed instead of integer due to lack of space.
    print '(I0)', i ! Auto-computed width
    print '(I0.4)', i ! the .4 signifies the number of digits to be printed, and since 4 < 6, this produces a series of asterisks.
    print '(I0.8)', i ! since 8 > 6, there are 0s added to the front of the integer to make it fit.

    print '(A8)', c
    print '(A4)', c ! String is cut.

    ! Real Value Formatting
    ! (Fx.y) where x is the width of the string and can be set to 0 and
    ! y is the number of digits after the decimal point. This does not
    ! represent numbers in E notation and can lead to cut numbers.
    print '(F6.2)', r ! This leads to rounding -> i.e. 1.24 and since this is only 4 long, there are 2 spaces in front.
    ! Note that the negative sign also counts as a string unit.
    
    ! (ew.dex) where w is width of string, d is number of digits after decimal, and x os the number of digits used for the exponent.
    print '(e8.2e2)', r2 !0.12E+06
    print '(es0.2)', r2 ! 1.23E+5 (0 w not supported in some compilers), es makes the decimal between 1 and 9
    print '(en0.3)', r2 ! 123.000E+3 (0 w not supported in some compilers), en converts to engineering notation (e+3, e+6, etc.)

    ! For logical values, Lw. Will always print F/T 
    
    ! General edit descriptor, Gw.d can be used for integer, real, logical and character values
    ! Simplest form is G0, where it will choose the appropriate width for the value.
    ! Although this is very convenient, for real values, the number of digits is compiler dependent.
    
    print '(es0.2, A1, I0)', r2, ' ', i ! Combining descriptors; Prints 1.23E+5 123456
    ! For multiple values of the same type:
    print '(/, *(es0.2))', r, r2, r, r2, r2 ! / is the newline indicator, * for an unknown number of real vars formatted as follows.
    print '(5es9.2)', r, r2, r, r2, r2 ! For only 5 real values
    
    ! Dynamic formatting of strings based on variable:
    ! integer :: nr_digits = 5
    ! write (fmt_str, "('(E', I0, '.', I0, ')')" nr_digits + 7, nr_digits 
    ! The resulting format would be (E12.5).
    
    ! Converting a read string into another datatype
    ! character(len=64) :: buffer
    ! integer :: nr_values, istat
    ! character(len=1024) :: msg
    
    ! read (buffer, fmt='(I64)', iostat=istat, iomsg=msg) nr_values
    
    
end program IO