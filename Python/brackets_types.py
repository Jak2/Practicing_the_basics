
#* []-these brackets are used when you are using list in python

#* ()-these bracket are used in many ways like in tuples, methods, passing argument etc

#* {}-these brackets are used when you are using dictionary in python

a=(1,2,3,4)
print(a)
print("printing a[0];",a[0])
print(type(a),"\n")

b=('11','22','33','44')
print(b)
print("printing b[0 to 2]",b[0:2])
print(type(b),"\n")

"""
c=(text,without,inverted,comas)
type=(c) #! text is not defined error
"""

d=('text','in','inverted comas')
print(d)
print("printing d[0 to 3]",d[0:3])
print(type(d),"\n")

e=[111,111,111,111]
print(e)
print("printing lists from e[0 to 3]",e[0:3])
print(type(e),"\n")

f=['222','222','222','222']
print(f)
print("printing lists from f[0 to 3]",f[0:3])
print(type(f),"\n")

"""
g=[text, without, inverted, comas ,square,brackets]
type(g) #! text is not defined error
"""

h=['square','bracketed','text','in','inverted','comas']
print(h)
print("printing lists from h[0 to 5]",h[0:5])
print(type(h),"\n")


#! print(a + b + d + e + f + h)
#! TypeError: can only concatenate tuple (not "list") to tuple

print("printing all the tuples\n",a+b+d,"\n")
print("printing all the lists\n",e+f+h,"\n")

#! ---------------------------------------------------------------------------

#? trying something different from the above this might be confusing so 
#? i am writing it in here
"""
#* student=(first=jak,second=naveen,third='sravanth',fourth=prabhas kamal,fifth=jayanth)
#!   student=(first=jak,second=naveen,third='sravanth',fourth=prabhas kamal,fifth=jayanth)
#!                 ^
# !         SyntaxError: invalid syntax

#* print[syudent[0]]
#* print(student[0].first)
"""

"""
student=(first='Jak',second='jay,)
print(student[0])
print(student[0].first)
#!     student=(first='Jak',second='jay,)
#!                   ^
#!   SyntaxError: invalid syntax
"""

hello={'a':1,'b':2}
print(hello)
# *print("printing 1st element of the dict",hello[1])
#! KeyError: 1
"""* A Python KeyError exception is what is raised when you try to access a key
        that isn't in a dictionary ( dict ).
     Python's official documentation says that the KeyError is raised when a mapping key is accessed 
        and isn't found in the mapping. 
     A mapping is a data structure that maps one set of values to another.
"""

