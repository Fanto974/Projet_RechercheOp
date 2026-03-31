from collections import deque

class Graphe:

    def __init__(self, aretes, n, m):
        self.aretes = aretes
        self.n = n
        self.m = m
        self.adj = {}

    def afficher(self):
        """Dessine le graphe biparti : fournisseurs en haut, clients en bas."""

        largeur = 120
        hauteur = 30
        grille = [[' '] * largeur for _ in range(hauteur)]

        ligne_F = 1
        ligne_C = hauteur - 2

        # Positions horizontales des fournisseurs
        pos_F = {}
        pas_F = largeur // (self.n + 1)
        for i in range(self.n):
            col = pas_F * (i + 1)
            pos_F[i] = col
            label = f"[P{i + 1}]"
            start = col - len(label) // 2
            for k, c in enumerate(label):
                if 0 <= start + k < largeur:
                    grille[ligne_F][start + k] = c

        # Positions horizontales des clients
        pos_C = {}
        pas_C = largeur // (self.m + 1)
        for j in range(self.m):
            col = pas_C * (j + 1)
            pos_C[j] = col
            label = f"[C{j + 1}]"
            start = col - len(label) // 2
            for k, c in enumerate(label):
                if 0 <= start + k < largeur:
                    grille[ligne_C][start + k] = c

        # Dessin des arêtes diagonales sans label
        for (i, j) in self.aretes:
            x0, y0 = pos_F[i], ligne_F + 1
            x1, y1 = pos_C[j], ligne_C - 1

            # Algorithme de Bresenham
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            sx = 1 if x1 > x0 else -1
            sy = 1 if y1 > y0 else -1
            err = dx - dy

            x, y = x0, y0
            while True:
                if 0 <= y < hauteur and 0 <= x < largeur:
                    if grille[y][x] == ' ':
                        if x0 == x1:
                            grille[y][x] = '|'
                        elif x0 < x1:
                            grille[y][x] = '\\'
                        else:
                            grille[y][x] = '/'
                if x == x1 and y == y1:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x += sx
                if e2 < dx:
                    err += dx
                    y += sy

        # Affichage
        print("\n" + "=" * largeur)
        print(" GRAPHE DE TRANSPORT".center(largeur))
        print("=" * largeur)
        for row in grille:
            print(''.join(row))
        print("=" * largeur + "\n")

    def construire_adjacence(self):
        """
        Construit la liste d'adjacence du graphe biparti sous forme de DICTIONNAIRE.

        """
        adj = {}
        for (i, j) in self.aretes:
            cle_fournisseur = f"P{i}"  # Sommet fournisseur
            cle_client = f"C{j}"  # Sommet client

            # Ajouter le client dans les voisins du fournisseur
            if cle_fournisseur not in adj:
                adj[cle_fournisseur] = []
            adj[cle_fournisseur].append(cle_client)

            # Ajouter le fournisseur dans les voisins du client (graphe non orienté)
            if cle_client not in adj:
                adj[cle_client] = []
            adj[cle_client].append(cle_fournisseur)

        self.adj = adj

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
        if not self.aretes:
            return False, []

        self.construire_adjacence()

        # Dictionnaires pour le BFS (au lieu de listes indexées par entier)
        visite = {}  # sommet -> True/False
        parent = {}  # sommet -> sommet parent (ou None pour la racine)

        # Initialiser tous les sommets comme non visités
        for sommet in self.adj:
            visite[sommet] = False
            parent[sommet] = None

        # Parcourir toutes les composantes connexes
        for depart in self.adj:
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
                for v in self.adj.get(u, []): # On met un .get pour ne pas avoir une erreur si u n'est pas dans le dico
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

    def test_connexite_bfs(self):
        """
        Teste si le graphe biparti formé par les arêtes de base est connexe.
        Utilise un dictionnaire pour la liste d'adjacence.

        Retourne :
            (est_connexe, composantes)
            est_connexe (bool)
            composantes (list of list) : chaque composante est une liste de sommets
                                         (clés de type "P0", "C1", etc.)
        """
        if not self.aretes:
            return False, []

        self.construire_adjacence()

        # Dictionnaire pour marquer les sommets visités
        visite = {sommet: False for sommet in self.adj}

        composantes = []

        for depart in self.adj:
            if visite[depart]:
                continue

            composante = []
            file = deque([depart])
            visite[depart] = True

            while file:
                u = file.popleft()
                composante.append(u)
                for v in self.adj.get(u, []):
                    if not visite.get(v, True):  # True par défaut = considéré comme visité
                        visite[v] = True
                        file.append(v)

            composantes.append(composante)

        est_connexe = len(composantes) == 1

        if not est_connexe:
            print(f"  Graphe NON connexe : {len(composantes)} composantes")
            for k, comp in enumerate(composantes):
                # Extraire les fournisseurs ("P0" -> 1) et clients ("C0" -> 1)
                fournisseurs = [int(s[1:]) + 1 for s in comp if s.startswith("P")]
                clients = [int(s[1:]) + 1 for s in comp if s.startswith("C")]
                print(f"    Composante {k + 1} : Fournisseurs {fournisseurs}, Clients {clients}")
        else:
            print("  Graphe connexe : OK")

        return est_connexe, composantes


