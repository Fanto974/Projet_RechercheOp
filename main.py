from problem import Problem

p = Problem("./files/test.txt")
p.repr_prob()
p.nord_ouest()
p.repr_prop()
p.graph_base()
print(p.detecter_cycle())