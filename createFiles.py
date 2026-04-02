# =============================================================================
# ÉTAPE 10 : CRÉATION DES FICHIERS .TXT DES 12 PROBLÈMES
# =============================================================================
import os

PROBLEMES = {
    1: {
        'n': 2, 'm': 2,
        'couts': [[30, 20], [10, 50]],
        'provisions': [100, 100],
        'commandes': [100, 100]
    },
    2: {
        'n': 2, 'm': 2,
        'couts': [[10, 20], [30, 10]],
        'provisions': [100, 100],
        'commandes': [100, 100]
    },
    3: {
        'n': 2, 'm': 2,
        'couts': [[30, 20], [10, 50]],
        'provisions': [600, 500],
        'commandes': [100, 1000]
    },
    4: {
        'n': 2, 'm': 2,
        'couts': [[30, 1], [1, 30]],
        'provisions': [600, 500],
        'commandes': [100, 1000]
    },
    5: {
        'n': 3, 'm': 3,
        'couts': [[5, 7, 8], [6, 8, 5], [6, 7, 7]],
        'provisions': [25, 25, 25],
        'commandes': [35, 20, 20]
    },
    6: {
        'n': 3, 'm': 4,
        'couts': [[11, 12, 10, 10], [17, 16, 15, 18], [19, 21, 20, 22]],
        'provisions': [60, 30, 90],
        'commandes': [50, 75, 30, 25]
    },
    7: {
        'n': 4, 'm': 2,
        'couts': [[50, 20], [10, 50], [50, 40], [45, 35]],
        'provisions': [100, 200, 100, 200],
        'commandes': [300, 300]
    },
    8: {
        'n': 5, 'm': 2,
        'couts': [[50, 20], [10, 50], [55, 40], [35, 45], [12, 8]],
        'provisions': [100, 200, 100, 200, 200],
        'commandes': [300, 500]
    },
    9: {
        'n': 7, 'm': 3,
        'couts': [
            [30, 20, 15],
            [10, 50, 2],
            [9, 10, 30],
            [6, 2, 29],
            [50, 40, 3],
            [5, 38, 27],
            [50, 4, 22]
        ],
        'provisions': [100, 100, 100, 100, 100, 100, 100],
        'commandes': [400, 200, 100]
    },
    10: {
        'n': 3, 'm': 7,
        'couts': [
            [300, 20, 15, 16, 17, 18, 20],
            [1, 50, 24, 30, 22, 27, 19],
            [50, 40, 30, 3, 25, 26, 3]
        ],
        'provisions': [500, 500, 2500],
        'commandes': [500, 500, 500, 500, 500, 500, 500]
    },
    11: {
        'n': 20, 'm': 10,
        'couts': [[i * 10 + j + 1 for j in range(10)] for i in range(20)],
        'provisions': [(i + 1) * 10 for i in range(20)],
        'commandes': [120, 140, 160, 180, 200, 220, 240, 260, 280, 300]
    },
    12: {
        'n': 10, 'm': 16,
        'couts': [],
        'provisions': [160] * 10,
        'commandes': [100] * 16
    }
}

# Construire la matrice des coûts du problème 12
# P1: 186 185 184 ... 171
# P2: 166 165 164 ... 151
# etc.
_starts_12 = [186, 166, 156, 136, 116, 96, 76, 56, 36, 16]
for i, start in enumerate(_starts_12):
    PROBLEMES[12]['couts'].append([start - j for j in range(16)])


def creer_fichier_probleme(num_probleme, dossier="files"):
    """
    Crée le fichier .txt pour un problème de transport donné.
    """
    if not os.path.exists(dossier):
        os.makedirs(dossier)

    pb = PROBLEMES[num_probleme]
    n, m = pb['n'], pb['m']
    couts = pb['couts']
    provisions = pb['provisions']
    commandes = pb['commandes']

    chemin = os.path.join(dossier, f"1-5-{num_probleme}.txt")

    with open(chemin, 'w') as f:
        f.write(f"{n} {m}\n")
        for i in range(n):
            ligne = " ".join(str(c) for c in couts[i])
            f.write(f"{ligne} {provisions[i]}\n")
        f.write(" ".join(str(c) for c in commandes) + "\n")

    return chemin


def creer_tous_les_fichiers(dossier="files"):
    """Crée les 12 fichiers .txt."""
    for num in range(1, 13):
        chemin = creer_fichier_probleme(num, dossier)
        print(f"Fichier créé : {chemin}")

