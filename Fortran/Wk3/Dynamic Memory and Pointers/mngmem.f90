program mean
    use, intrinsic :: iso_fortran_env
    implicit none
    integer, parameter :: nr_runs = 5
    integer :: nr_values
    integer :: run 
    real, dimension(:), allocatable :: values ! Deferred shape array
    ! Alternate definition
    ! real, allocatable :: values(:)

    ! Runtime Char Allocation
    ! character(len=:), allocatable :: buffer
    ! integer :: buffer_len
    ! allocate (character(len=buffer_len) :: buffer, stat=istat)

    ! Array cloning
    ! real, dimension(0:10) :: values
    ! real, dimension(:), allocatable :: tmp_values
    ! allocate(tmp_values, source=values)

    ! Procedure Allocation
    ! subroutine qsort(values)
    !     implicit none
    !     real, dimension(:), intent(inout) :: values
    ! This works if values is already allocated

    ! subroutine allocate_array(array, array_size, msg, init)
        ! use, intrinsic :: iso_fortran_env, only : error_unit
        ! implicit none
        ! real, dimension(:), allocatable, intent(inout) :: array
        ! if (allocated(array)) &
        ! deallocate(array)


    ! This allows one to pass an allocatable variable "array"
    ! If it is already allocated, it will first be deallocated before
    ! the program continues.

    ! Elements of a user defined type can also be allocated
    ! allocate(stats%values(100))

    call get_arguments(nr_values)
    
    do run = 1, nr_runs
        values = init_values(nr_values)
        print '(F10.3)', sum(values)/size(values)
    enddo
    deallocate(values)
contains
    function init_values(nr_values) result(values)
        implicit none
        integer, value :: nr_values
        real, dimension(:), allocatable :: values
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
