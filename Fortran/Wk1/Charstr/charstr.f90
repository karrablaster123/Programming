program charstr
        use, intrinsic :: iso_fortran_env
        character :: c
        character(len = 5) :: str
        character(len = 5) :: str2
        character(len=10) :: catstr
        c = 'c'
        str = 'hahaa'

        print *, c
        print *, str        

        ! This leads to amputation of later characters
        str = 'OyyBlyat'
        str2 = 'OyyBlyat'
        catstr = str // str2
        print *, str
        print *, (str == str2)
        print *, catstr
end program charstr
