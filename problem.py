from graphe import Graphe
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
        self.graph = None
        self.potentiels = ([], [])

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
        self.proposition = proposition
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
        self.graph = Graphe(aretes, self.n, self.m)
        self.graph.afficher()


    def est_non_degeneree(self):
        """
        Vérifie que la proposition a exactement n + m - 1 arêtes de base.
        Une proposition non dégénérée est un arbre couvrant du graphe biparti.
        """
        nb_aretes = 0
        for i in range(self.n):
            for j in range(self.m):
                if self.proposition[i][j] is not None and self.proposition[i][j] != -1:
                    nb_aretes += 1

        attendu = self.n + self.m - 1
        print(f"  Nombre d'arêtes de base : {nb_aretes} (attendu : {attendu})")
        return nb_aretes == attendu

    def maximiser_transport_cycle(self, cycle):
        """
        Maximise le transport sur un cycle.

        Le cycle est alternativement + et - :
        - La première arête (l'arête ajoutée) est +
        - Les suivantes alternent -, +, -, +, ...

        delta = min des valeurs sur les arêtes -

        Retourne :
            proposition modifiée
            delta (int) : la quantité transférée
            aretes_supprimees (list) : arêtes tombées à 0
        """
        if not cycle:
            return self.proposition, 0, []

        # Identifier les arêtes + et -
        aretes_plus = []
        aretes_moins = []
        for k, (i, j) in enumerate(cycle):
            if k % 2 == 0:
                aretes_plus.append((i, j))
            else:
                aretes_moins.append((i, j))

        print("  Arêtes + :", [(i + 1, j + 1) for (i, j) in aretes_plus])
        print("  Arêtes - :", [(i + 1, j + 1) for (i, j) in aretes_moins])

        # Calculer delta
        delta = float('inf')
        for (i, j) in aretes_moins:
            val = self.proposition[i][j]
            if val is not None and val != -1:
                delta = min(delta, val)
            else:
                delta = 0

        print(f"  delta = {delta}")

        # Appliquer le transfert
        for (i, j) in aretes_plus:
            if self.proposition[i][j] is None or self.proposition[i][j] == -1:
                self.proposition[i][j] = delta
            else:
                self.proposition[i][j] += delta

        aretes_supprimees = []
        for (i, j) in aretes_moins:
            self.proposition[i][j] -= delta
            if self.proposition[i][j] == 0:
                aretes_supprimees.append((i, j))

        # Supprimer UNE arête à 0 (la première trouvée dans les arêtes -)
        if aretes_supprimees:
            # On supprime la dernière arête à 0 dans les arêtes -
            i_sup, j_sup = aretes_supprimees[-1]
            self.proposition[i_sup][j_sup] = None
            print(f"  Arête supprimée : ({i_sup + 1}, {j_sup + 1})")

            # S'il y a d'autres arêtes à 0, on les garde à 0 (dégénérescence)
            if len(aretes_supprimees) > 1:
                print(f"  Attention : dégénérescence, arêtes restantes à 0 : "
                      f"{[(i + 1, j + 1) for (i, j) in aretes_supprimees[:-1]]}")

        return self.proposition, delta, aretes_supprimees

    def rendre_connexe(self, composantes):
        """
        Rend le graphe connexe en ajoutant des arêtes de coût minimum
        entre les composantes.
        Les arêtes ajoutées ont une valeur de 0 (dégénérescence).
        On trie les arêtes hors-base par coût croissant et on ajoute
        celles qui relient deux composantes différentes.

        Les composantes contiennent des clés "P0", "C1", etc. (format dictionnaire).
        """
        # Créer un dictionnaire sommet -> numéro de composante
        comp_de = {}
        for k, comp in enumerate(composantes):
            for s in comp:
                comp_de[s] = k

        # Lister toutes les arêtes hors-base triées par coût croissant
        aretes_hors_base = []
        for i in range(self.n):
            for j in range(self.m):
                if self.proposition[i][j] is None or self.proposition[i][j] == -1:
                    aretes_hors_base.append((self.couts[i][j], i, j))
        aretes_hors_base.sort()

        nb_composantes = len(composantes)

        for (cout, i, j) in aretes_hors_base:
            cle_f = f"P{i}"  # Clé du fournisseur dans le dictionnaire
            cle_c = f"C{j}"  # Clé du client dans le dictionnaire

            if cle_f in comp_de and cle_c in comp_de:
                if comp_de[cle_f] != comp_de[cle_c]:
                    # Cette arête relie deux composantes -> l'ajouter
                    self.proposition[i][j] = 0
                    print(f"  Ajout arête ({i + 1},{j + 1}) avec coût {cout} pour relier les composantes")

                    # Fusionner les composantes
                    ancien = comp_de[cle_c]
                    nouveau = comp_de[cle_f]
                    for s in comp_de:
                        if comp_de[s] == ancien:
                            comp_de[s] = nouveau

                    nb_composantes -= 1
                    if nb_composantes == 1:
                        break
            elif cle_f not in comp_de:
                self.proposition[i][j] = 0
                if cle_c in comp_de:
                    comp_de[cle_f] = comp_de[cle_c]
                print(f"  Ajout arête ({i + 1},{j + 1}) pour intégrer P{i + 1}")
            elif cle_c not in comp_de:
                self.proposition[i][j] = 0
                if cle_f in comp_de:
                    comp_de[cle_c] = comp_de[cle_f]
                print(f"  Ajout arête ({i + 1},{j + 1}) pour intégrer C{j + 1}")

    def calculer_potentiels(self):
        """
        Calcule les potentiels u_i et v_j tels que u_i + v_j = a_ij
        pour chaque arête de base.

        Retourne :
            u (list) : potentiels des fournisseurs
            v (list) : potentiels des clients
        """
        u = [None] * self.n
        v = [None] * self.m

        # Construire les adjacences
        adj_fournisseur = [[] for _ in range(self.n)]  # Pour chaque fournisseur, liste des clients en base
        adj_client = [[] for _ in range(self.m)]  # Pour chaque client, liste des fournisseurs en base

        for i in range(self.n):
            for j in range(self.m):
                if self.proposition[i][j] is not None and self.proposition[i][j] != -1:
                    adj_fournisseur[i].append(j)
                    adj_client[j].append(i)

        # Fixer u[0] = 0
        u[0] = 0

        # BFS pour propager les potentiels
        file = deque()
        file.append(('u', 0))  # On commence par le fournisseur 0

        while file:
            type_sommet, idx = file.popleft()

            if type_sommet == 'u':
                # Fournisseur idx : u[idx] est connu
                for j in adj_fournisseur[idx]:
                    if v[j] is None:
                        v[j] = self.couts[idx][j] - u[idx]
                        file.append(('v', j))
            else:
                # Client idx : v[idx] est connu
                for i in adj_client[idx]:
                    if u[i] is None:
                        u[i] = self.couts[i][idx] - v[idx]
                        file.append(('u', i))

        self.potentiels = (u, v)