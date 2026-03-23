from problem import Problem

p = Problem("./files/test.txt")
p.repr_prob()
p.nord_ouest()
p.repr_prop()
print(p.coutTotal)
p.balas_hammer()
p.repr_prop()
print(p.coutTotal)