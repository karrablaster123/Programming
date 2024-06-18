program hello_world
!       This line is a comment
!       The following line tells the compiler that all variables must be explicitly
!       defined. If I had incorrectly spelt the variable name and not used this, 
!       Fortran would not throw an error.
        implicit none

        character(len=30), parameter :: message = 'Hello World! I am a string'
        print *, 'Hello world!'
        print *, message
end program hello_world
