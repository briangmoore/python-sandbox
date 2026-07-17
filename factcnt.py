import math
M=int(input("Enter an integer M: "))
print("M= ",M)
K=2
print("Finding factors other than 1 and M")
for N in range(2,int(M/2)+1,1):
#    print("N= ",N)
    if math.modf(M/N)[0]==0:
#        print(N," is a factor")
        K+=1
print(K," factors")
if K==2:
    print(M," is prime")