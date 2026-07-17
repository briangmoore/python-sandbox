# python scripts echoing caculator programs
# bdaysim2 runs bday function and creates a list of Ns for each simulation

import sys
M=int(sys.argv[1])
L4 = []

def bdaysim():
    import math
    import random
    L3 = []
    N = random.randint(1,365)
    while True:
        L3.append(N)
        N = random.randint(1,365)
        if N in L3:
            L3.append(N)
#            print(L3)
            return len(L3)

for i in range(M):
    L4.append(bdaysim())
print(L4)

import numpy as np

print("Mean:", np.mean(L4))
print("Median:", np.median(L4))
print("Std Dev:", np.std(L4))
print("Variance:", np.var(L4))
print("Q1:", np.percentile(L4, 25))
print("Q3:", np.percentile(L4, 75))
print("Min:", np.min(L4))
print("Max:", np.max(L4))

import matplotlib.pyplot as plt

plt.hist(L4, bins=np.arange(min(L4), max(L4) + 2))
plt.show()

        