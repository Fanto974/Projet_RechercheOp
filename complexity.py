import argparse
import json
import os
import random
import sys
import time
import contextlib
import tempfile

from readAndDisplayFunc import afficher_resultats
from createFiles import creer_fichier_probleme

# Répartition du travail sur 4 machines.
# Les grandes tailles dominants, on les isole chacune sur une machine.
# Les reps sont réduites pour les grandes tailles (compromis temps/statistiques).
DISTRIBUTION_MACHINES = {
    1: {'tailles': [10000],            'reps': {10000: 1}},
    2: {'tailles': [4000],             'reps': {4000: 4}},
    3: {'tailles': [4000],             'reps': {4000: 4}},
    4: {'tailles': [1000],             'reps': {1000: 30}},
    5: {'tailles': [1000],             'reps': {1000: 30}},
    6: {'tailles': [10, 40, 100, 400], 'reps': {10: 100, 40: 100, 100: 100, 400: 100}},
    7: {'tailles': [10000],            'reps': {10000: 1}},
    8: {'tailles': [10000],            'reps': {10000: 1}},
}


def generer_probleme_aleatoire(taille_n):
    n = m = taille_n
    couts = [[random.randint(1, 100) for _ in range(m)] for _ in range(n)]
    temp = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]
    provisions = [sum(temp[i]) for i in range(n)]
    commandes = [sum(temp[i][j] for i in range(n)) for j in range(n)]
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
    tmp.write(f"{n} {m}\n")
    for i in range(n):
        tmp.write(" ".join(str(c) for c in couts[i]) + f" {provisions[i]}\n")
    tmp.write(" ".join(str(c) for c in commandes) + "\n")
    tmp.close()
    return tmp.name


def _charger_json(chemin):
    with open(chemin, encoding='utf-8') as f:
        data = json.load(f)
    return {
        'tailles': data['tailles'],
        'theta_NO': {int(k): v for k, v in data['theta_NO'].items()},
        'theta_BH': {int(k): v for k, v in data['theta_BH'].items()},
        't_NO':     {int(k): v for k, v in data['t_NO'].items()},
        't_BH':     {int(k): v for k, v in data['t_BH'].items()},
    }


def _sauvegarder_json(resultats, chemin):
    data = {
        'tailles':   resultats['tailles'],
        'theta_NO': {str(k): v for k, v in resultats['theta_NO'].items()},
        'theta_BH': {str(k): v for k, v in resultats['theta_BH'].items()},
        't_NO':     {str(k): v for k, v in resultats['t_NO'].items()},
        't_BH':     {str(k): v for k, v in resultats['t_BH'].items()},
    }
    chemin_tmp = chemin + '.tmp'
    with open(chemin_tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    os.replace(chemin_tmp, chemin)


def mesurer_complexite(tailles, reps_par_taille, chemin_sauvegarde=None):
    from problem import Problem

    resultats = {
        'tailles':  tailles,
        'theta_NO': {},
        'theta_BH': {},
        't_NO':     {},
        't_BH':     {},
    }

    if chemin_sauvegarde and os.path.exists(chemin_sauvegarde):
        print("Reprise depuis le checkpoint...", file=sys.stderr)
        sauvegarde = _charger_json(chemin_sauvegarde)
        for cle in ('theta_NO', 'theta_BH', 't_NO', 't_BH'):
            resultats[cle] = sauvegarde[cle]

    for taille in tailles:
        nb_reps   = reps_par_taille.get(taille, 100)
        deja_fait = len(resultats['theta_NO'].get(taille, []))

        if deja_fait >= nb_reps:
            print(f"Taille {taille:6d} : déjà {deja_fait}/{nb_reps} reps — ignorée.", file=sys.stderr)
            continue

        print(f"\n=== Taille n={taille} ({nb_reps} reps, {deja_fait} déjà faites) ===", file=sys.stderr)

        for cle in ('theta_NO', 'theta_BH', 't_NO', 't_BH'):
            if taille not in resultats[cle]:
                resultats[cle][taille] = []

        for rep in range(deja_fait, nb_reps):
            if rep % 10 == 0:
                print(f"  Répétition {rep + 1}/{nb_reps}", file=sys.stderr)

            chemin = generer_probleme_aleatoire(taille)
            try:
                with contextlib.redirect_stdout(open(os.devnull, 'w')):
                    p_no = Problem(chemin)
                    t0 = time.perf_counter()
                    p_no.nord_ouest()
                    t1 = time.perf_counter()
                resultats['theta_NO'][taille].append(t1 - t0)

                with contextlib.redirect_stdout(open(os.devnull, 'w')):
                    p_bh = Problem(chemin)
                    t0 = time.perf_counter()
                    p_bh.balas_hammer()
                    t1 = time.perf_counter()
                resultats['theta_BH'][taille].append(t1 - t0)

                with contextlib.redirect_stdout(open(os.devnull, 'w')):
                    t0 = time.perf_counter()
                    try:
                        p_no.methode_marche_pied()
                    except Exception:
                        pass
                    t1 = time.perf_counter()
                resultats['t_NO'][taille].append(t1 - t0)

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

            # Sauvegarde fréquente pour les grandes tailles, toutes les 10 reps sinon
            if chemin_sauvegarde:
                if taille >= 1000 or (rep + 1) % 10 == 0:
                    _sauvegarder_json(resultats, chemin_sauvegarde)

        # Sauvegarde garantie après chaque taille complète
        if chemin_sauvegarde:
            _sauvegarder_json(resultats, chemin_sauvegarde)
            print(f"  => Checkpoint sauvegardé : {chemin_sauvegarde}", file=sys.stderr)

    return resultats


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Étude de complexité — transport')
    parser.add_argument('--machine', type=int, choices=[1, 2, 3, 4, 5, 6, 7, 8], required=True,
                        help='Numéro de machine (1 à 4)')
    parser.add_argument('--reps', type=int, default=None,
                        help='Forcer le nombre de répétitions pour toutes les tailles')
    args = parser.parse_args()

    config = DISTRIBUTION_MACHINES[args.machine]
    tailles = config['tailles']
    reps_par_taille = config['reps'].copy()
    if args.reps is not None:
        reps_par_taille = {t: args.reps for t in tailles}

    chemin_sauvegarde = f"resultats_machine_{args.machine}.json"

    print(f"Machine {args.machine} — tailles : {tailles}", file=sys.stderr)
    print(f"Répétitions par taille : {reps_par_taille}", file=sys.stderr)

    res = mesurer_complexite(tailles, reps_par_taille, chemin_sauvegarde=chemin_sauvegarde)
    _sauvegarder_json(res, chemin_sauvegarde)
    print(f"\nRésultats finaux sauvegardés dans {chemin_sauvegarde}", file=sys.stderr)
    afficher_resultats(res)
