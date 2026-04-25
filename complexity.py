import os
import random
import sys
import time
import contextlib
import tempfile
import io
import re

from readAndDisplayFunc import *
from createFiles import creer_fichier_probleme


def generer_probleme_aleatoire(taille_n):
    """
    Génère un fichier de problème de transport aléatoire équilibré de taille n x n
    et retourne son chemin.

    Retourne :
        chemin (str) : chemin vers le fichier .txt généré
    """
    n = m = taille_n

    couts = [[random.randint(1, 100) for _ in range(m)] for _ in range(n)]

    temp = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]
    provisions = [sum(temp[i]) for i in range(n)]
    commandes = [sum(temp[i][j] for i in range(n)) for j in range(n)]

    # Écriture dans un fichier temporaire au format attendu par Problem
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
    tmp.write(f"{n} {m}\n")
    for i in range(n):
        ligne = " ".join(str(c) for c in couts[i])
        tmp.write(f"{ligne} {provisions[i]}\n")
    tmp.write(" ".join(str(c) for c in commandes) + "\n")
    tmp.close()

    return tmp.name


def mesurer_complexite(tailles, nb_repetitions=100, silencieux=True):
    """
    Mesure les temps d'exécution pour différentes tailles de problèmes.

    Paramètres :
        tailles (list) : liste des valeurs de n à tester
        nb_repetitions (int) : nombre de répétitions par taille
        silencieux (bool) : si True, supprime l'affichage pendant les mesures

    Retourne :
        resultats (dict) : dictionnaire avec les temps mesurés
    """
    from problem import Problem

    resultats = {
        'tailles': tailles,
        'theta_NO': {},
        'theta_BH': {},
        't_NO': {},
        't_BH': {},
    }

    for taille in tailles:
        print(f"\n=== Taille n = {taille} ===", file=sys.stderr)
        resultats['theta_NO'][taille] = []
        resultats['theta_BH'][taille] = []
        resultats['t_NO'][taille] = []
        resultats['t_BH'][taille] = []

        for rep in range(nb_repetitions):
            if rep % 10 == 0:
                print(f"  Répétition {rep + 1}/{nb_repetitions}", file=sys.stderr)

            chemin = generer_probleme_aleatoire(taille)

            try:
                # Mesure Nord-Ouest
                with contextlib.redirect_stdout(open(os.devnull, 'w')):
                    p_no = Problem(chemin)
                    t0 = time.perf_counter()
                    p_no.nord_ouest()
                    t1 = time.perf_counter()
                resultats['theta_NO'][taille].append(t1 - t0)

                # Mesure Balas-Hammer
                with contextlib.redirect_stdout(open(os.devnull, 'w')):
                    p_bh = Problem(chemin)
                    t0 = time.perf_counter()
                    p_bh.balas_hammer()
                    t1 = time.perf_counter()
                resultats['theta_BH'][taille].append(t1 - t0)

                # Mesure marche-pied après Nord-Ouest
                with contextlib.redirect_stdout(open(os.devnull, 'w')):
                    t0 = time.perf_counter()
                    try:
                        p_no.methode_marche_pied()
                    except Exception:
                        pass
                    t1 = time.perf_counter()
                resultats['t_NO'][taille].append(t1 - t0)

                # Mesure marche-pied après Balas-Hammer
                with contextlib.redirect_stdout(open(os.devnull, 'w')):
                    t0 = time.perf_counter()
                    try:
                        p_bh.methode_marche_pied()
                    except Exception:
                        pass
                    t1 = time.perf_counter()
                resultats['t_BH'][taille].append(t1 - t0)

            finally:
                os.remove(chemin)

    return resultats

class TeeBuffer:
    def __init__(self, original):
        self.original = original
        self.buffer = io.StringIO()

    def write(self, data):
        self.original.write(data)
        self.original.flush()
        self.buffer.write(data)

    def flush(self):
        self.original.flush()

    def getvalue(self):
        return self.buffer.getvalue()


# Remplace la fin du script par :
tee_out = TeeBuffer(sys.stdout)
tee_err = TeeBuffer(sys.stderr)

with contextlib.redirect_stdout(tee_out), contextlib.redirect_stderr(tee_err):
    res = mesurer_complexite([10])
    afficher_resultats(res)

with open("resultats.txt", "w", encoding="utf-8") as f:
    f.write(tee_out.getvalue())
    f.write(tee_err.getvalue())

print("Résultats copiés dans 'resultats.txt'")