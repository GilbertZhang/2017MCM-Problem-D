import numpy as np

import random
import scipy.stats as sci
print np.random.normal([0,0.1])

print range(3)

def equal_ele(list1):
    for i in range(len(list1)-1):
        if list1[i] != list1[i+1]:
            return False
    return True

print equal_ele([1,2,1])
print int(random.random()*3)

import simpy


print 32.305588 * np.random.weibull(2.172682,100)

print float("inf")