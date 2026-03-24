# Le fichier .txt est organisé ainsi :
#   Ligne 1 : n m  (nombre de fournisseurs, nombre de clients)
#   Lignes 2 à n+1 : a_i1 a_i2 ... a_im P_i  (coûts + provision)
#   Dernière ligne : C_1 C_2 ... C_m  (commandes)
#
# Pseudo-code :
#   Ouvrir le fichier
#   Lire n et m
#   Pour i de 1 à n :
#       Lire les m coûts et la provision P_i
#   Lire les m commandes C_j
#   Retourner n, m, matrice_couts, provisions, commandes

def lire_fichier(path):
    """
    Lit un fichier .txt contenant un problème de transport.

    Paramètres :
        path (str) : path vers le fichier .txt

    Retourne :
        n (int) : nombre de fournisseurs
        m (int) : nombre de clients
        couts (list[list[int]]) : matrice des coûts unitaires (n x m)
        provisions (list[int]) : provisions de chaque fournisseur
        commandes (list[int]) : commandes de chaque client
    """
    with open(path, 'r') as f:
        lignes = f.readlines()

    # Première ligne : n et m
    premiere_ligne = lignes[0].strip().split()
    n = int(premiere_ligne[0])
    m = int(premiere_ligne[1])

    couts = []
    provisions = []

    # Lignes 2 à n+1 : coûts + provision
    for i in range(1, n + 1):
        valeurs = list(map(int, lignes[i].strip().split()))
        # Les m premières valeurs sont les coûts, la dernière est la provision
        couts.append(valeurs[:m])
        provisions.append(valeurs[m])

    # Dernière ligne : commandes
    commandes = list(map(int, lignes[n + 1].strip().split()))

    return n, m, couts, provisions, commandes



def largeur_col(matrice, provisions, commandes, m, en_tete_ligne="P"):
    """Calcule la largeur nécessaire pour chaque colonne."""
    # Largeur pour les noms de lignes (P1, P2, etc.)
    larg_nom = max(len(f"{en_tete_ligne}{i + 1}") for i in range(len(matrice))) + 1
    larg_nom = max(larg_nom, len("Commandes") + 1)

    # Largeur pour chaque colonne de données
    largeurs = []
    for j in range(m):
        w = len(f"C{j + 1}")
        for i in range(len(matrice)):
            val = matrice[i][j]
            if val is None:
                w = max(w, 1)
            else:
                w = max(w, len(str(val)))
        if commandes is not None:
            w = max(w, len(str(commandes[j])))
        largeurs.append(w + 2)

    # Largeur pour la colonne provisions
    larg_prov = len("Provisions")
    if provisions is not None:
        for p in provisions:
            larg_prov = max(larg_prov, len(str(p)))
    larg_prov += 2

    return larg_nom, largeurs, larg_prov

def afficher_graphe(aretes, n, m):
    """Dessine le graphe biparti : fournisseurs en haut, clients en bas."""

    largeur = 120
    hauteur = 30
    grille = [[' '] * largeur for _ in range(hauteur)]

    ligne_F = 1
    ligne_C = hauteur - 2

    # Positions horizontales des fournisseurs
    pos_F = {}
    pas_F = largeur // (n + 1)
    for i in range(n):
        col = pas_F * (i + 1)
        pos_F[i] = col
        label = f"[P{i+1}]"
        start = col - len(label) // 2
        for k, c in enumerate(label):
            if 0 <= start + k < largeur:
                grille[ligne_F][start + k] = c

    # Positions horizontales des clients
    pos_C = {}
    pas_C = largeur // (m + 1)
    for j in range(m):
        col = pas_C * (j + 1)
        pos_C[j] = col
        label = f"[C{j+1}]"
        start = col - len(label) // 2
        for k, c in enumerate(label):
            if 0 <= start + k < largeur:
                grille[ligne_C][start + k] = c

    # Dessin des arêtes diagonales sans label
    for (i, j) in aretes:
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


def construire_adjacence(aretes):
    """
    Construit la liste d'adjacence du graphe biparti sous forme de DICTIONNAIRE.

    """
    adj = {}
    for (i, j) in aretes:
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

    return adj