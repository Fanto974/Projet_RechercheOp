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

def afficher_potentiels(potentiels_u, potentiels_v, n, m):
    """
    Affiche les potentiels u_i (fournisseurs) et v_j (clients).
    u_i + v_j = a_ij pour les arêtes de base.
    """
    print("\n  POTENTIELS :")
    print("  Fournisseurs (u) :", end="")
    for i in range(n):
        print(f"  u{i+1}={potentiels_u[i]}", end="")
    print()
    print("  Clients (v)      :", end="")
    for j in range(m):
        print(f"  v{j+1}={potentiels_v[j]}", end="")
    print("\n")


def afficher_table_potentiels_marginaux(couts, potentiels_u, potentiels_v, proposition, n, m):
    """
    Affiche :
    - La table des coûts potentiels : E_ij = u_i + v_j
    - La table des coûts marginaux  : M_ij = a_ij - E_ij (seulement pour les non-base)

    Les coûts marginaux ne sont calculés que pour les arêtes hors-base.
    Pour les arêtes de base, M_ij = 0 par construction.
    """
    # Table des coûts potentiels
    print("  TABLE DES COÛTS POTENTIELS (E_ij = u_i + v_j) :")
    larg_nom = max(len(f"P{i + 1}") for i in range(n)) + 1
    largeurs = []
    for j in range(m):
        w = len(f"C{j + 1}")
        for i in range(n):
            val = potentiels_u[i] + potentiels_v[j]
            w = max(w, len(str(val)))
        largeurs.append(w + 2)

    en_tete = " " * larg_nom
    for j in range(m):
        en_tete += f"{'C' + str(j + 1):>{largeurs[j]}}"
    print(en_tete)
    print("-" * len(en_tete))

    for i in range(n):
        ligne = f"{'P' + str(i + 1):<{larg_nom}}"
        for j in range(m):
            val = potentiels_u[i] + potentiels_v[j]
            ligne += f"{val:>{largeurs[j]}}"
        print(ligne)
    print()

    # Table des coûts marginaux
    print("  TABLE DES COÛTS MARGINAUX (M_ij = a_ij - E_ij) :")
    marginaux = [[None] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            e_ij = potentiels_u[i] + potentiels_v[j]
            marginaux[i][j] = couts[i][j] - e_ij

    # Recalculer les largeurs pour les marginaux
    largeurs_m = []
    for j in range(m):
        w = len(f"C{j + 1}")
        for i in range(n):
            if proposition[i][j] is not None and proposition[i][j] != -1:
                w = max(w, 1)  # Pour "0" ou "*"
            else:
                w = max(w, len(str(marginaux[i][j])))
        largeurs_m.append(w + 2)

    en_tete = " " * larg_nom
    for j in range(m):
        en_tete += f"{'C' + str(j + 1):>{largeurs_m[j]}}"
    print(en_tete)
    print("-" * len(en_tete))

    meilleure_arete = None
    meilleur_marginal = 0

    for i in range(n):
        ligne = f"{'P' + str(i + 1):<{larg_nom}}"
        for j in range(m):
            if proposition[i][j] is not None and proposition[i][j] != -1:
                # Arête de base : marginal = 0
                ligne += f"{'*':>{largeurs_m[j]}}"
            else:
                val = marginaux[i][j]
                ligne += f"{val:>{largeurs_m[j]}}"
                if val < meilleur_marginal:
                    meilleur_marginal = val
                    meilleure_arete = (i, j)
        print(ligne)
    print()

    return marginaux, meilleure_arete, meilleur_marginal