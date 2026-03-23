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



