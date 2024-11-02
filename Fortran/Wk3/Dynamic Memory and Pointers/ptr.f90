program pointers
    implicit none
    
    integer, target :: a, b
    integer, pointer :: ptr

    ! Define linked list using pointers
    type, public :: list_item_t
        private
        real :: value
        type(list_item_t), pointer :: next => null()
    end type list_item_t

    nullify(ptr) !Initialises pointer to null
    print *, associated(ptr) ! Returns a boolean value depending on if the pointer has a target or not
    ! prints F
    
    p => a
    print *, associated(ptr) ! True
    print *, associated(ptr, a) ! True
    print *, associated(ptr, b) ! False

    ptr => b
    print *, associated(ptr) ! True
    print *, associated(ptr, a) ! False
    print *, associated(ptr, b) ! True

    p => null() ! Another way to nullify pointer
    print *, associated(ptr) ! False

end program pointers