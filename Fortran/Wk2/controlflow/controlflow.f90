program control

        implicit none
        
        ! select case (item/variable)
        !       case (this) (Tests if item == this)
        !               do if this
        !       case (that)
        !               do if that
        !       case default
        !               Similar to else case       
        ! end select

        ! array based if statements
        ! real, dimension(n) :: masses, charges, probabilities
        ! call random_number(probabilities)
        ! where (probabilities < 0.5)
        !       masses = proton_mass
        !       charges = proton_charge
        ! elsewhere (You can add a logical statement here and more elsewheres)
        !       masses = electron_mass
        !       charges = electron_charge
        ! endwhere

        ! In a simple case with a single elsewhere like above, you can use 
        ! the merge statement
        ! call random_number(probabilities)
        ! masses = merge(proton_mass, electron_mass, probabilities < 0.5)
        ! charges = merge(proton_charge, electron_charge, probabilities < 0.5)
       

        ! See forall and do concurrent 
        
end program control
