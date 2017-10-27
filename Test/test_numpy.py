import numpy as np

a = np.array([0,0.5,1.0,1.5,2.0])

print(type(a))

print(a[:2])

print(a.sum())
print(a.std())

print(a.cumsum())

print(a * 2)

print(a ** 2)

print(np.sqrt(a))




b = np.array([a,a*2])
print(b)

print(b[0])

print(b[0,2])

print(b.sum())

print(b.sum(axis=0))

print(b.sum(axis=1))





