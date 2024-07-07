module stats_mod
    implicit none

    private ! Sets default access. Anything that should be accessible should be flagged with public

    type, public :: stats_t
        real :: sum, sum2
        integer :: n
    end type stats_t 

    public :: add_stats_value, init_stats, mean_stats ! needed to show the subroutines to the public

contains

    subroutine init_stats(stat)
        implicit none
        type(stats_t), intent(out) :: stats

        stats = stats_t(0.0, 0.0, 0)
    end subroutine init_stats

    subroutine add_stats_value(stats, value)
        implicit none
        type(stats_t), intent(inout) :: stats
        real, value :: value

        stats%sum = stats%sum + value
        stats%sum2 = stats%sum2 + value **2
        stats%n = stats%n + 1
    end subroutine add_stats_value

    function mean_stats(stats) result(mean_value)
        use, intrinsic :: iso_fortran_env
        implicit none
        type(stats_t), intent(in) :: stats
        real :: mean_value

        if ( stats%n ==0 ) then
            write (unit = error_unit, fmt='(A)') 'Error: Not Enough Data'
            stop 1
        endif

        associate (sum => stats%sum, n => stats%n)
            mean_value=sum/n
        end associate
        
    end function mean_stats

end module stats_mod