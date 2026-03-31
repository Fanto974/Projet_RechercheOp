from problem import Problem
from readAndDisplayFunc import afficher_potentiels, afficher_table_potentiels_marginaux

FICHIER = "./files/test.txt"

# =============================================================================
# Chargement et affichage du problème
# =============================================================================
print("\n" + "#" * 70)
print("  CHARGEMENT DU PROBLÈME")
print("#" * 70)

p = Problem(FICHIER)
print(f"  {p.n} fournisseurs x {p.m} clients")
print(f"  Total provisions = {sum(p.provisions)}, Total commandes = {sum(p.commandes)}")
p.repr_prob()

# =============================================================================
# TEST 1 : Méthode Nord-Ouest
# =============================================================================
print("\n" + "#" * 70)
print("  TEST 1 : MÉTHODE NORD-OUEST")
print("#" * 70)

p.nord_ouest()
p.repr_prop("PROPOSITION NORD-OUEST")
print(f"  Coût total : {p.coutProp}")

print("\n--- Non-dégénérescence ---")
p.est_non_degeneree()

print("\n--- Graphe de base / Connexité / Cycles ---")
p.graph_base()

est_connexe, composantes = p.graph.test_connexite_bfs()

if not est_connexe:
    print("\n--- Rendre connexe ---")
    p.rendre_connexe(composantes)
    p.repr_prop("PROPOSITION APRÈS RENDRE CONNEXE")
    p.graph_base()
    p.graph.test_connexite_bfs()
has_cycle, cycle = p.graph.detecter_cycle()
while has_cycle:
    print(f"  Cycle détecté : {[(i+1, j+1) for (i, j) in cycle]}")
    print("\n--- Maximisation sur le cycle ---")
    p.maximiser_transport_cycle(cycle)
    p.repr_prop("PROPOSITION APRÈS MAXIMISATION")
    print(f"  Coût total après maximisation : {p.coutProp}")
    p.graph_base()
    has_cycle, cycle = p.graph.detecter_cycle()
print("  Aucun cycle → proposition acyclique")

print("\n--- Calcul des potentiels ---")
p.calculer_potentiels()
u, v = p.potentiels
afficher_potentiels(u, v, p.n, p.m)
afficher_table_potentiels_marginaux(p.couts, u, v, p.proposition, p.n, p.m)

# =============================================================================
# TEST 2 : Méthode Balas-Hammer
# =============================================================================
print("\n" + "#" * 70)
print("  TEST 2 : MÉTHODE BALAS-HAMMER")
print("#" * 70)

p2 = Problem(FICHIER)
p2.balas_hammer()
p2.repr_prop("PROPOSITION BALAS-HAMMER")
print(f"  Coût total : {p2.coutProp}")

print("\n--- Non-dégénérescence ---")
p2.est_non_degeneree()

print("\n--- Graphe de base / Connexité / Cycles ---")
p2.graph_base()

est_connexe2, composantes2 = p2.graph.test_connexite_bfs()

if not est_connexe2:
    print("\n--- Rendre connexe ---")
    p2.rendre_connexe(composantes2)
    p2.repr_prop("PROPOSITION APRÈS RENDRE CONNEXE")
    p2.graph_base()
    p2.graph.test_connexite_bfs()
has_cycle2, cycle2 = p2.graph.detecter_cycle()
while has_cycle2:
    print(f"  Cycle détecté : {[(i+1, j+1) for (i, j) in cycle2]}")
    print("\n--- Maximisation sur le cycle ---")
    p2.maximiser_transport_cycle(cycle2)
    p2.repr_prop("PROPOSITION APRÈS MAXIMISATION")
    print(f"  Coût total après maximisation : {p2.coutProp}")
    p2.graph_base()
    has_cycle2, cycle2 = p2.graph.detecter_cycle()
print("  Aucun cycle → proposition acyclique")

print("\n--- Calcul des potentiels ---")
p2.calculer_potentiels()
u2, v2 = p2.potentiels
afficher_potentiels(u2, v2, p2.n, p2.m)
afficher_table_potentiels_marginaux(p2.couts, u2, v2,p2.proposition, p2.n, p2.m)

# =============================================================================
# COMPARAISON FINALE
# =============================================================================
print("\n" + "#" * 70)
print("  COMPARAISON DES MÉTHODES INITIALES")
print("#" * 70)
print(f"  Coût Nord-Ouest   : {p.coutProp}")
print(f"  Coût Balas-Hammer : {p2.coutProp}")
meilleure = "Nord-Ouest" if p.coutProp <= p2.coutProp else "Balas-Hammer"
print(f"  Meilleure proposition initiale : {meilleure}")
