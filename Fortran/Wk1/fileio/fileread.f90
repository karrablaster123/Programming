program files
        
        use, intrinsic :: iso_fortran_env
        implicit none

        integer, parameter :: nr_values = 10, io_error = 1
        character(len=50), parameter :: filename = 'data.txt'
        integer :: unit_nr, stat
        character(len=1024) :: msg
        real :: x = 5.1

        open (newunit = unit_nr, file = filename, access='sequential', &
                action='read', status='old', form='formatted', &
                iostat=stat, iomsg=msg)
        if (stat /= 0) then
                write (unit=error_unit, fmt='(A)') msg
                stop io_error       
        endif

        do
                read (unit=unit_nr, fmt=*, iostat=stat, iomsg = msg) x
                if (stat == iostat_end) then
                        exit
                elseif (stat > 0) then
                        write (unit = error_unit, fmt='(A)') msg
                        stop io_error
                endif
                write (unit=output_unit, fmt='(F8.1)') x**2
        enddo
        close (unit_nr, iostat=stat, iomsg=msg)

        if (stat /= 0) then
                write (unit=error_unit, fmt='(A)') msg
                stop io_error
        endif
        
        
end program files
