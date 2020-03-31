
#* for number in a list means 
#* number = alist and this runs in loop that's all
#* for better understanding 
#* see this n2 for n from 0to5 program down this line 

alist=[1,2,3,4,6]
number=3 #* this is a number but alist is a list 
for number in alist:
    print(number)




#* n2 for n from 0to5
for n in [0,1,2,3,4,5]:
    square = n**2
    print(n,"square is ",square)
    print(n,"square of ",n,square) #* this will obviously run in between each time 
                                   #*   the 1st print runs

print(n,"square of ",n,square) #* prints square of 5


for x in range (1,10):
    print("\n\n\n",x,"\n\n\n")

print("\n\n\n")

another_list=[2333,3323,111]
for x in another_list:
    print(x)

_2nd_list=[2,22,222,2222,22222]
for x in _2nd_list:
    print(_2nd_list)
#! the above _2nd_list printed 5 rows since the data is of 5 col

_3rd_list=[3,33,333,3333]
print(_3rd_list)
#! the above prints _3rd_list only once


_4th_list=[4,44,444,4444]
for x in _4th_list:
    print(_4th_list)
#! the above prints _4th_list four times



"""
#! this will give error since it cannot compare numbers with objects
#! i might be wrong her reg why this is happening but time and experience
#! can answer this
apples, oranges, mangoes= 1,2,3
for x in apples:
    print(x)
"""