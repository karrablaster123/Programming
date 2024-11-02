program mean
    use, intrinsic :: iso_fortran_env
    implicit none
    integer, parameter :: nr_runs = 5
    integer :: nr_values
    integer :: run 
    real, dimension(:), pointer :: values ! Deferred shape array

    call get_arguments(nr_values)
    
    do run = 1, nr_runs
        values => init_values(nr_values)
        print '(F10.3)', sum(values)/size(values)
        deallocate(values) ! See difference in positioning
    enddo
    ! Never double deallocate -> will cause a runtime error.
   

contains
    function init_values(nr_values) result(values)
        implicit none
        integer, value :: nr_values
        real, dimension(:), pointer :: values
        integer :: status

        allocate(values(nr_values), stat=status)
        if ( status /= 0 ) then
            write (unit=error_unit, fmt='(A, I0, A)') 'error: cannot allocate ', nr_values, ' values'
            stop 2
        endif 
        call random_number(values)
    end function init_values

    subroutine get_arguments(nr_values)
        implicit none
        integer, intent(out) :: nr_values
        integer :: status
        character(len=1024) :: buffer, msg

        if (command_argument_count() == 1) then
            call get_command_argument(1, buffer)
            read (buffer, fmt=*, iostat=status, iomsg=msg) nr_values
            if (status /= 0) then
                write (unit=error_unit, fmt='(2A)') 'error: ', msg
                stop 1
            endif
        else
            nr_values = 10
        endif
    end subroutine get_arguments
end program mean
