from z3 import *

x = Int("x") # pour simplifier l'appel à x
y = Int("y") # pour simplifier l'appel à y
s = Solver() # encapsulation d'un solveur
s.add(x ** 2 + y ** 2 < 5) # une contrainte
sol = []
while s.check() == sat:
    m = s.model()
    sol.append(m)
    #This solution works and then is excluded in order to find a new solution if possible
    s.add(Or(x!=m[x],y!=m[y]))
    print("asserted constraints...")
    for c in s.assertions():
        print(c)
    print(s.check())

print(sol)
print(f"There are {len(sol)} solutions")