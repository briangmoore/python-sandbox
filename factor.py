import math
M=int(input("Enter integer: "))

for N in range(2,M-1):
    if math.modf(M/N)[0] == 0:
        print(N)
