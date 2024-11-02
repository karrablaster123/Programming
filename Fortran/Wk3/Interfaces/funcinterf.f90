module quad_func_interface_mod

    interface
        ! This interface is for the quadrature solver. 
        ! It defines what type of function is passed into
        ! the solver for robust error handling
        function quad_func_t(x) result(f)
            use intrinsic :: iso_fortran_env, only: DP => REAL64
            implicit none

            real(kind=DP), value :: x
            real(kind=DP) :: f
        end function quad_func_t
    end interface

end module quad_func_interface_mod