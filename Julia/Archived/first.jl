# My first variable
x = 10
print(x+1)
x + 1

x = x+1

#Math Symbols using Latex \delta then by hitting tab
δ = 11
α² = 13
#pi is constant, you cannot redefine it.

#pi = 4 would not work

#same with predefined functions such as sqrt

typeof(1)
print("\n")
print(1)

#When used in multiplication, false acts as a strong zero:
print("\n")
show(NaN * false)
print("\n")
show(false* Inf)

#Boolean operations
x = false
y = !x
print("\n")
show(x)
print("\n")
show(y)
# && and || also work as usual

# Supports the following updating operations +=  -=  *=  /=  \=  ÷=  %=  ^=
# Note the existence of \ which is used to inverse divide: x\y = y/x
# Note that dot operators exist too for vector operations

#=
==	equality
!=, ≠	inequality
<	less than
<=, ≤	less than or equal to
>	greater than
>=, ≥	greater than or equal to

Positive zero is equal but not greater than negative zero.
Inf is equal to itself and greater than everything else except NaN.
-Inf is equal to itself and less than everything else except NaN.
NaN is not equal to, not less than, and not greater than anything, including itself.


isequal(x, y)	x and y are identical
isfinite(x)	x is a finite number
isinf(x)	x is infinite
isnan(x)	x is not a number

isqual considers NaNs to be equal to each other and considers oppositely signed zeroes to be unequal to each other.
=#

#Mathematical functions (like any Julia function) can be applied in "vectorized" fashion to arrays and other collections with the dot syntax f.(A), e.g. sin.(A) will compute the sine of each element of an array A.