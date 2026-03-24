from readAndDisplayFunc import *
from collections import deque

class Problem :

    def __init__(self, path):
        """
        n : Nombre de fournisseurs
        m : Nombre de clients
        couts : matrice représentant le problème initial
        provisions : liste des fournisseurs
        commandes : liste des commandes clients
        propositions : matrice de la proposition en cours
        """
        self.n, self.m, self.couts, self.provisions, self.commandes = lire_fichier(path)
        self.proposition = [[]]
        self.coutProp = 0
        self.graph = []

    def repr_prob(self):
        """
        Affiche la matrice des coûts unitaires de transport.

        Format :
                  C1    C2    ...   Cm    Provisions
        P1        a11   a12   ...   a1m   P1
        ...
        Pn        an1   an2   ...   anm   Pn
        Commandes C1    C2    ...   Cm
        """
        print("\n" + "=" * 60)
        print("  REPRESENTATION DU PROBLEME DE TRANSPORT")
        print("=" * 60)

        larg_nom, largeurs, larg_prov = largeur_col(self.couts, self.provisions, self.commandes, self.m)

        # En-tête
        en_tete = " " * larg_nom
        for j in range(self.m):
            en_tete += f"{'C' + str(j + 1):>{largeurs[j]}}"
        en_tete += f"{'Provisions':>{larg_prov}}"
        print(en_tete)
        print("-" * len(en_tete))

        # Lignes des fournisseurs
        for i in range(self.n):
            ligne = f"{'P' + str(i + 1):<{larg_nom}}"
            for j in range(self.m):
                ligne += f"{self.couts[i][j]:>{largeurs[j]}}"
            ligne += f"{self.provisions[i]:>{larg_prov}}"
            print(ligne)

        # Ligne des commandes
        print("-" * len(en_tete))
        ligne_cmd = f"{'Commandes':<{larg_nom}}"
        for j in range(self.m):
            ligne_cmd += f"{self.commandes[j]:>{largeurs[j]}}"
        print(ligne_cmd)
        print()

    def repr_prop(self, titre="PROPOSITION DE TRANSPORT"):
        """
        Affiche la proposition initiale.
        Les cases à None ou -1 sont affichées comme '.' (non utilisées).
        """
        print("\n" + "=" * 60)
        print(f"  {titre}")
        print("=" * 60)

        # Préparer une matrice affichable
        mat_aff = []
        for i in range(self.n):
            ligne = []
            for j in range(self.m):
                val = self.proposition[i][j]
                if val is None or val == -1:
                    ligne.append(".")
                else:
                    ligne.append(str(val))
            mat_aff.append(ligne)

        # Calculer les largeurs
        larg_nom = max(len(f"P{i + 1}") for i in range(self.n)) + 1
        larg_nom = max(larg_nom, len("Commandes") + 1)

        largeurs = []
        for j in range(self.m):
            w = len(f"C{j + 1}")
            for i in range(self.n):
                w = max(w, len(mat_aff[i][j]))
            w = max(w, len(str(self.commandes[j])))
            largeurs.append(w + 2)

        larg_prov = len("Provisions")
        for p in self.provisions:
            larg_prov = max(larg_prov, len(str(p)))
        larg_prov += 2

        # En-tête
        en_tete = " " * larg_nom
        for j in range(self.m):
            en_tete += f"{'C' + str(j + 1):>{largeurs[j]}}"
        en_tete += f"{'Provisions':>{larg_prov}}"
        print(en_tete)
        print("-" * len(en_tete))

        # Lignes
        for i in range(self.n):
            ligne = f"{'P' + str(i + 1):<{larg_nom}}"
            for j in range(self.m):
                ligne += f"{mat_aff[i][j]:>{largeurs[j]}}"
            ligne += f"{self.provisions[i]:>{larg_prov}}"
            print(ligne)

        # Commandes
        print("-" * len(en_tete))
        ligne_cmd = f"{'Commandes':<{larg_nom}}"
        for j in range(self.m):
            ligne_cmd += f"{self.commandes[j]:>{largeurs[j]}}"
        print(ligne_cmd)
        print()


    def nord_ouest(self):
        # Principe : on parcourt la matrice de haut-gauche (nord-ouest) vers bas-droite.
        # À chaque étape, on remplit la case (i, j) avec le minimum entre la provision
        # restante du fournisseur i et la commande restante du client j.
        #
        # Pseudo-code :
        #   i = 0, j = 0
        #   prov = copie(provisions), cmd = copie(commandes)
        #   Tant que i < n et j < m :
        #       quantite = min(prov[i], cmd[j])
        #       B[i][j] = quantite
        #       prov[i] -= quantite
        #       cmd[j] -= quantite
        #       Si prov[i] == 0 : i += 1
        #       Si cmd[j] == 0  : j += 1
        """
        Calcule la proposition initiale par la méthode Nord-Ouest.
        """
        self.proposition = [[None] * self.m for _ in range(self.n)]
        prov = self.provisions[:]
        cmd = self.commandes[:]

        i, j = 0, 0

        print("\n--- Déroulement de Nord-Ouest ---")

        while i < self.n and j < self.m:
            quantite = min(prov[i], cmd[j])
            self.proposition[i][j] = quantite
            print(f"  Case ({i + 1},{j + 1}) : min(prov={prov[i]}, cmd={cmd[j]}) = {quantite}")

            prov[i] -= quantite
            cmd[j] -= quantite

            if prov[i] == 0 and cmd[j] == 0:
                # Les deux sont épuisés : on avance en diagonale
                # Cas de dégénérescence possible
                i += 1
                j += 1
            elif prov[i] == 0:
                i += 1
            else:
                j += 1
        self.cout_total()



    def balas_hammer(self):
        # Principe : à chaque étape, on calcule la "pénalité" de chaque ligne et colonne.
        # La pénalité est la différence entre les deux plus petits coûts non barrés.
        # On choisit la ligne ou colonne de pénalité maximale, puis on affecte le maximum
        # possible à la case de coût minimum dans cette ligne/colonne.
        #
        # Pseudo-code :
        #   Tant qu'il reste des lignes et colonnes actives :
        #       Pour chaque ligne active : pénalité = 2e_min - 1er_min des coûts non barrés
        #       Pour chaque colonne active : idem
        #       Sélectionner la ligne ou colonne de pénalité maximale
        #       Dans cette ligne/colonne, trouver la case de coût minimum
        #       Affecter min(prov[i], cmd[j]) à cette case
        #       Mettre à jour provisions et commandes
        #       Barrer la ligne ou colonne épuisée
        """
        Calcule la proposition initiale par la méthode Balas-Hammer.

        Retourne :
            proposition (list[list]) : matrice n x m
        """
        proposition = [[None] * self.m for _ in range(self.n)]
        prov = self.provisions[:]
        cmd = self.commandes[:]

        lignes_actives = set(range(self.n))
        colonnes_actives = set(range(self.m))

        print("\n--- Déroulement de Balas-Hammer ---")
        etape = 0

        while lignes_actives and colonnes_actives:
            etape += 1
            print(f"\n  Étape {etape} :")

            # Calculer les pénalités des lignes
            penalites_lignes = {}
            for i in lignes_actives:
                couts_actifs = []
                for j in colonnes_actives:
                    couts_actifs.append((self.couts[i][j], j))
                couts_actifs.sort()     # On trie la liste
                if len(couts_actifs) >= 2:
                    penalites_lignes[i] = couts_actifs[1][0] - couts_actifs[0][0] # les 2 premiers éléments sont donc les plus petits couts de la ligne
                elif len(couts_actifs) == 1:
                    penalites_lignes[i] = couts_actifs[0][0]
                else:
                    penalites_lignes[i] = 0

            # Calculer les pénalités des colonnes
            penalites_colonnes = {}
            for j in colonnes_actives:
                couts_actifs = []
                for i in lignes_actives:
                    couts_actifs.append((self.couts[i][j], i))
                couts_actifs.sort()
                if len(couts_actifs) >= 2:
                    penalites_colonnes[j] = couts_actifs[1][0] - couts_actifs[0][0]
                elif len(couts_actifs) == 1:
                    penalites_colonnes[j] = couts_actifs[0][0]
                else:
                    penalites_colonnes[j] = 0

            # Afficher les pénalités
            print("    Pénalités lignes  :", {f"P{i + 1}": penalites_lignes[i] for i in sorted(penalites_lignes)})
            print("    Pénalités colonnes:", {f"C{j + 1}": penalites_colonnes[j] for j in sorted(penalites_colonnes)})

            # Trouver la pénalité maximale
            max_pen_ligne = max(penalites_lignes.values()) if penalites_lignes else -1
            max_pen_col = max(penalites_colonnes.values()) if penalites_colonnes else -1

            if max_pen_ligne >= max_pen_col:
                # Choisir parmi les lignes de pénalité max
                lignes_max = [i for i in penalites_lignes if penalites_lignes[i] == max_pen_ligne]
                print(f"    Pénalité max = {max_pen_ligne} sur ligne(s) : {['P' + str(i + 1) for i in lignes_max]}")

                # Prendre la première ligne de pénalité max
                i_choisi = lignes_max[0]

                # Trouver le coût minimum dans cette ligne parmi les colonnes actives
                min_cout = float('inf')
                j_choisi = None
                for j in colonnes_actives:
                    if self.couts[i_choisi][j] < min_cout:
                        min_cout = self.couts[i_choisi][j]
                        j_choisi = j
            else:
                # Choisir parmi les colonnes de pénalité max
                colonnes_max = [j for j in penalites_colonnes if penalites_colonnes[j] == max_pen_col]
                print(f"    Pénalité max = {max_pen_col} sur colonne(s) : {['C' + str(j + 1) for j in colonnes_max]}")

                j_choisi = colonnes_max[0]

                # Trouver le coût minimum dans cette colonne parmi les lignes actives
                min_cout = float('inf')
                i_choisi = None
                for i in lignes_actives:
                    if self.couts[i][j_choisi] < min_cout:
                        min_cout = self.couts[i][j_choisi]
                        i_choisi = i

            # Affecter la quantité
            quantite = min(prov[i_choisi], cmd[j_choisi])
            proposition[i_choisi][j_choisi] = quantite
            print(f"    -> Affectation case ({i_choisi + 1},{j_choisi + 1}) : coût={min_cout}, quantité={quantite}")

            prov[i_choisi] -= quantite
            cmd[j_choisi] -= quantite

            # Barrer ligne ou colonne épuisée
            if prov[i_choisi] == 0 and cmd[j_choisi] == 0:  # Si la ligne et la colonne sont épuisée on enlève les 2
                lignes_actives.discard(i_choisi)
                colonnes_actives.discard(j_choisi)
                print(f"    Ligne P{i_choisi + 1} ET Colonne C{j_choisi + 1} épuisées")
            elif prov[i_choisi] == 0:
                lignes_actives.discard(i_choisi)
                print(f"    Ligne P{i_choisi + 1} épuisée")
            else:
                colonnes_actives.discard(j_choisi)
                print(f"    Colonne C{j_choisi + 1} épuisée")
        self.cout_total()


    def cout_total(self):
        """
        Calcule le coût total d'une proposition de transport.
        """
        total = 0
        for i in range(self.n):
            for j in range(self.m):
                if self.proposition[i][j] is not None and self.proposition[i][j] != -1:
                    total += self.couts[i][j] * self.proposition[i][j]
        self.coutProp = total

    def graph_base(self):
        """Liste la liste des arêtes du graphe de base."""
        aretes = []
        for i in range(self.n):
            for j in range(self.m):
                if self.proposition[i][j] is not None and self.proposition[i][j] != -1:
                    aretes.append((i, j))
        self.graph = aretes
        afficher_graphe(self.graph, self.n, self.m)

    def detecter_cycle(self):
        """
        Détecte un cycle dans le graphe biparti par BFS.
        Utilise un dictionnaire pour la liste d'adjacence.

        Retourne :
            (has_cycle, cycle_aretes)
            has_cycle (bool) : True si un cycle est détecté
            cycle_aretes (list) : liste des arêtes (i,j) formant le cycle
                                  (indices fournisseur/client numériques)
        """
        if not self.graph:
            return False, []

        adj = construire_adjacence(self.graph)

        # Dictionnaires pour le BFS (au lieu de listes indexées par entier)
        visite = {}  # sommet -> True/False
        parent = {}  # sommet -> sommet parent (ou None pour la racine)

        # Initialiser tous les sommets comme non visités
        for sommet in adj:
            visite[sommet] = False
            parent[sommet] = None

        # Parcourir toutes les composantes connexes
        for depart in adj:
            # On évite de faire le traitement plusieurs fois pour le même noeud
            if visite[depart]:
                continue

            # initialisation du parcours en largeur avec une file
            file = deque([depart])
            visite[depart] = True

            while file:
                # Tant qu'il reste des éléments dans la file on continue notre parcour en largeur
                u = file.popleft()

                # On parcours tous les sommets adjacents au sommet sur lequel on est
                for v in adj.get(u, []): # On met un .get pour ne pas avoir une erreur si u n'est pas dans le dico
                    if not visite[v]:
                        # Sommet non encore visité : on le découvre et on l'ajoute à la liste
                        visite[v] = True
                        parent[v] = u
                        file.append(v)

                    elif v != parent[u]:
                        # si le sommet est déjà visité ET ce n'est pas le parent de ce sommet. (pcq le parent d'un sommet est aussi un somment adjacent à celui ci donc on veut pas le prendre en comtpe)
                        # => CYCLE DÉTECTÉ entre u et v
                        print(f"  Cycle détecté entre sommets {u} et {v}")

                        # --- Reconstruction du cycle ---

                        # 1) Collecter les parents de u
                        parents_u = set()
                        actual = u
                        while actual is not None:
                            parents_u.add(actual)
                            actual = parent[actual]

                        # 2) Remonter depuis v jusqu'à trouver le parent commun
                        chemin_v = []
                        y = v
                        while y not in parents_u:
                            chemin_v.append(y)
                            y = parent[y]
                        parent_commun = y
                        chemin_v.append(parent_commun)

                        # 3) Remonter depuis u jusqu'à l'ancêtre commun
                        chemin_u = []
                        x = u
                        while x != parent_commun:
                            chemin_u.append(x)
                            x = parent[x]
                        chemin_u.append(parent_commun)

                        # 4) Assembler le cycle : u -> ancêtre -> v
                        cycle_sommets = chemin_u + chemin_v[::-1][1:]

                        # 5) Convertir les sommets ("P0", "C1", ...) en arêtes (i, j)
                        cycle_aretes = []
                        for k in range(len(cycle_sommets)):
                            s1 = cycle_sommets[k]
                            s2 = cycle_sommets[(k + 1) % len(cycle_sommets)]

                            # Identifier qui est le fournisseur et qui est le client
                            if s1.startswith("P") and s2.startswith("C"):
                                i = int(s1[1:])
                                j = int(s2[1:])
                                cycle_aretes.append((i, j))
                            elif s1.startswith("C") and s2.startswith("P"):
                                j = int(s1[1:])
                                i = int(s2[1:])
                                cycle_aretes.append((i, j))

                        print(f"  Cycle (arêtes) : {[(i + 1, j + 1) for (i, j) in cycle_aretes]}")
                        return True, cycle_aretes

        return False, []
