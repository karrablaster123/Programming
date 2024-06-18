#region Imaginary
#Define imaginary numbers using im 
f = 1 + 2im
print((2-3im)f)
print("\n" * string(f/(1-2im)))

#Basic imaginary functions
print("\n" * string(real(f)))
print("\n" * string(imag(f)))
print("\n" * string(conj(f)))
print("\n" * string(abs(f)))
print("\n" * string(abs2(f)))
print("\n" * string(angle(f)))

#Cannot do sqrt(-1).
#Instead
print("\n" * string(sqrt(Complex(-1))))

#You cannot do the literal numeric coefficient notation here: such as a + bim like you would do x + 3x
#Instead
a = 1
b = 8
print("\n" * string(a + b*im))
#endregion

#region Rational numbers in Julia
a = 2//3 #a = 2/3 (literal value and not an approximation)
#these rational numbers are automatically reduced by dividing by their least common factors
b = 5//-15 # b = -1/3 
#We can use functions to obtain the numerator and denominator
numerator(a) # returns 2
denominator(b) #returns 3
#Logical evaluation of rational numbers
2//3 == 6//9 #true
#Convert to floating point by casting
float(a) #returns 0.666666...

print("\n" * string(3//4 == 0.75)) # true!

#We can construct infinite rational numbers
c = 2//0
#We cannot construct NaN rational numbers
# c = 0//0
#endregion

#region Strings
c = 'x'
print("\n" * string(typeof(c))) #Char
print("\n" * string(Int(c))) #Number value of character
print("\n" * string(typeof(Int(c)))) #Int64
#For unicode characters
print("\n" * '\u2200') #Unicode code of a character
#Similar to C, you can do comparisons using char values and limited arithmetic
#String Basics
str = "\nHello, world!."
print(str)
print("""\nContains "quote" characters""")

#endregion

#region functions
function g(x,y)
    x + y
end
h(x, y) = x + y

f = g
print("\n" * string(g(2, 3)) * "\n" * string(h(2, 3)) * "\n" * string(f(2, 3)))
#As with variables, we can also use symbols to denote functions
α(x, y) = x^2 + y^2 - x - y
α(2, 3)
#Define argument type in declaration:
β(x::Integer) = sqrt(x)
β(1)
# β(2.3) Will cause an error to be thrown
# return keyword works like other languages
# except:
    #Specifying return type using function g(...)::Integer will force the return type to be an integer
    #return nothing
#Operators are functions
print("\n" * string(1 + 2 + 3)) # same as
print("\n" * string(+(1, 2, 3))) # same As
f = +
print("\n" * string(f(1, 2, 3)))
    
#endregion

