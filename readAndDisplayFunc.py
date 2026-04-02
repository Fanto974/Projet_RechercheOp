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


import matplotlib.pyplot as plt
import numpy as np


def afficher_resultats(resultats):
    """
    Affiche les résultats de l'étude de complexité :
      - 6 nuages de points (θ_NO, θ_BH, t_NO, t_BH, θ_NO+t_NO, θ_BH+t_BH)
      - 6 courbes d'enveloppe supérieure (pire des cas)
      - Identification du type de complexité
      - Ratio (θ_NO+t_NO)/(θ_BH+t_BH) et son max

    Paramètres :
        resultats (dict) : dictionnaire retourné par mesurer_complexite()
    """
    tailles = resultats['tailles']

    # =========================================================================
    # 1) Calcul des valeurs combinées θ+t pour chaque répétition
    # =========================================================================
    somme_NO = {}
    somme_BH = {}
    for n in tailles:
        somme_NO[n] = [
            resultats['theta_NO'][n][i] + resultats['t_NO'][n][i]
            for i in range(len(resultats['theta_NO'][n]))
        ]
        somme_BH[n] = [
            resultats['theta_BH'][n][i] + resultats['t_BH'][n][i]
            for i in range(len(resultats['theta_BH'][n]))
        ]

    # Dictionnaire des 6 séries à tracer
    series = {
        r'$\theta_{NO}(n)$': resultats['theta_NO'],
        r'$\theta_{BH}(n)$': resultats['theta_BH'],
        r'$t_{NO}(n)$': resultats['t_NO'],
        r'$t_{BH}(n)$': resultats['t_BH'],
        r'$(\theta_{NO}+t_{NO})(n)$': somme_NO,
        r'$(\theta_{BH}+t_{BH})(n)$': somme_BH,
    }

    # =========================================================================
    # 2) Nuages de points — 6 graphiques
    # =========================================================================
    fig1, axes1 = plt.subplots(2, 3, figsize=(18, 10))
    fig1.suptitle("Nuages de points — 100 réalisations par taille", fontsize=14)

    for ax, (label, data) in zip(axes1.flat, series.items()):
        for n in tailles:
            x = [n] * len(data[n])
            ax.scatter(x, data[n], s=8, alpha=0.4)
        ax.set_xlabel("n")
        ax.set_ylabel("Temps (s)")
        ax.set_title(label)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.grid(True, which='both', linestyle='--', alpha=0.5)

    fig1.tight_layout(rect=[0, 0, 1, 0.95])
    fig1.savefig("nuages_de_points.png", dpi=150)
    print("=> nuages_de_points.png sauvegardé")

    # =========================================================================
    # 3) Enveloppe supérieure (pire des cas) — 6 courbes sur un même graphique
    # =========================================================================
    fig2, ax2 = plt.subplots(figsize=(10, 7))
    ax2.set_title("Complexité dans le pire des cas (enveloppe supérieure)", fontsize=13)

    for label, data in series.items():
        maxima = [max(data[n]) for n in tailles]
        ax2.plot(tailles, maxima, marker='o', label=label)

    ax2.set_xlabel("n")
    ax2.set_ylabel("Temps max (s)")
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.legend()
    ax2.grid(True, which='both', linestyle='--', alpha=0.5)
    fig2.tight_layout()
    fig2.savefig("pire_des_cas.png", dpi=150)
    print("=> pire_des_cas.png sauvegardé")

    # =========================================================================
    # 4) Identification du type de complexité
    # =========================================================================
    print("\n" + "=" * 70)
    print("IDENTIFICATION DU TYPE DE COMPLEXITÉ (pire des cas)")
    print("=" * 70)

    types_complexite = {
        'O(log n)':      lambda n: np.log(n),
        'O(n)':          lambda n: n,
        'O(n log n)':    lambda n: n * np.log(n),
        'O(n²)':         lambda n: n ** 2,
        'O(n³)':         lambda n: n ** 3,
    }

    for label, data in series.items():
        maxima = np.array([max(data[n]) for n in tailles])
        ns = np.array(tailles, dtype=float)

        print(f"\n  {label} :")
        print(f"    {'n':>8s} | {'t_max (s)':>12s}")
        print(f"    {'-'*8}-+-{'-'*12}")
        for i, n in enumerate(tailles):
            print(f"    {n:8d} | {maxima[i]:12.6f}")

        # On cherche le meilleur fit : t_max / f(n) devrait être ~ constant
        meilleur_type = None
        meilleure_variance = float('inf')

        for nom, f in types_complexite.items():
            ratios = maxima / f(ns)
            # Coefficient de variation (écart-type relatif) — plus petit = meilleur fit
            if np.mean(ratios) > 0:
                cv = np.std(ratios) / np.mean(ratios)
                if cv < meilleure_variance:
                    meilleure_variance = cv
                    meilleur_type = nom

        print(f"    => Complexité estimée : {meilleur_type}  (CV = {meilleure_variance:.4f})")

    # =========================================================================
    # 5) Ratio (θ_NO + t_NO) / (θ_BH + t_BH) — comparaison
    # =========================================================================
    fig3, axes3 = plt.subplots(1, 2, figsize=(14, 6))

    # 5a) Nuage du ratio
    ax_nuage = axes3[0]
    ax_nuage.set_title("Ratio (θ_NO+t_NO) / (θ_BH+t_BH) — nuage")
    for n in tailles:
        ratios_n = []
        for i in range(len(somme_NO[n])):
            if somme_BH[n][i] > 0:
                ratios_n.append(somme_NO[n][i] / somme_BH[n][i])
        ax_nuage.scatter([n] * len(ratios_n), ratios_n, s=8, alpha=0.4)
    ax_nuage.set_xlabel("n")
    ax_nuage.set_ylabel("Ratio")
    ax_nuage.set_xscale('log')
    ax_nuage.axhline(y=1, color='red', linestyle='--', alpha=0.6, label='ratio = 1')
    ax_nuage.legend()
    ax_nuage.grid(True, which='both', linestyle='--', alpha=0.5)

    # 5b) Max du ratio par n
    ax_max = axes3[1]
    ax_max.set_title("Ratio max par taille n")
    ratio_max = []
    for n in tailles:
        ratios_n = []
        for i in range(len(somme_NO[n])):
            if somme_BH[n][i] > 0:
                ratios_n.append(somme_NO[n][i] / somme_BH[n][i])
        ratio_max.append(max(ratios_n) if ratios_n else 0)
    ax_max.plot(tailles, ratio_max, marker='o', color='darkblue')
    ax_max.set_xlabel("n")
    ax_max.set_ylabel("Ratio max")
    ax_max.set_xscale('log')
    ax_max.axhline(y=1, color='red', linestyle='--', alpha=0.6, label='ratio = 1')
    ax_max.legend()
    ax_max.grid(True, which='both', linestyle='--', alpha=0.5)

    fig3.tight_layout()
    fig3.savefig("ratio_comparaison.png", dpi=150)
    print("\n=> ratio_comparaison.png sauvegardé")

    # =========================================================================
    # 6) Discussion
    # =========================================================================
    print("\n" + "=" * 70)
    print("DISCUSSION")
    print("=" * 70)
    print("Si le ratio max > 1 pour les grandes tailles, alors Nord-Ouest + marche-pied")
    print("est globalement plus lent que Balas-Hammer + marche-pied dans le pire des cas.")
    print("Si le ratio max < 1, c'est l'inverse.")
    print("Un ratio proche de 1 signifie que les deux approches ont des performances similaires.")

    plt.show()
