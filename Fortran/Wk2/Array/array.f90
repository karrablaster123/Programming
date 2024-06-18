program array
        
        implicit none
        real, dimension(3) :: vector, vector_alpha, vector_beta
        integer :: i
        vector = 1.0
        print *, vector
        
        vector(2) = 5.7
        vector(1) = 2*vector(2)
        print *, vector
        print *, 3.0 + vector
        print *, 2.5*vector
        print *, vector**2
        print *, dot_product(vector, vector)
        
         
        vector_alpha = [3.0, 5.0, 7.0]
        vector_beta = [(0.5*i - 1.0, i=1, 3)]
        print *, vector_alpha
        print *, vector_beta
        print *, vector_alpha + vector_beta
        print *, vector_alpha * vector_beta
        print *, dot_product(vector_alpha, vector_beta)
        print *, size(vector_alpha)
        print *, sum(vector_alpha)
end program array
