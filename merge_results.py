"""
Fusionne les fichiers resultats_machine_*.json produits par complexity.py
et génère les graphiques combinés.

Usage :
    python merge_results.py                          # lit tous les resultats_machine_*.json
    python merge_results.py res1.json res2.json ...  # fichiers explicites
"""

import glob
import json
import sys

from readAndDisplayFunc import afficher_resultats


def charger_json(chemin):
    with open(chemin, encoding='utf-8') as f:
        data = json.load(f)
    return {
        'tailles':  data['tailles'],
        'theta_NO': {int(k): v for k, v in data['theta_NO'].items()},
        'theta_BH': {int(k): v for k, v in data['theta_BH'].items()},
        't_NO':     {int(k): v for k, v in data['t_NO'].items()},
        't_BH':     {int(k): v for k, v in data['t_BH'].items()},
    }


def fusionner(liste_resultats):
    tailles_candidates = sorted({t for r in liste_resultats for t in r['tailles']})
    cles = ('theta_NO', 'theta_BH', 't_NO', 't_BH')

    fusionne = {'tailles': [], **{c: {} for c in cles}}

    for t in tailles_candidates:
        merged = {c: [] for c in cles}
        for r in liste_resultats:
            for c in cles:
                merged[c].extend(r[c].get(t, []))

        # On n'inclut une taille que si toutes les 4 séries ont des données
        if all(len(merged[c]) > 0 for c in cles):
            fusionne['tailles'].append(t)
            for c in cles:
                fusionne[c][t] = merged[c]
        else:
            print(f"  Avertissement : taille {t} ignorée (données incomplètes ou absentes)",
                  file=sys.stderr)

    return fusionne


if __name__ == '__main__':
    if len(sys.argv) > 1:
        fichiers = sys.argv[1:]
    else:
        fichiers = sorted(glob.glob('resultats_machine_*.json'))

    if not fichiers:
        print("Aucun fichier résultat trouvé.")
        print("Usage : python merge_results.py [fichier1.json fichier2.json ...]")
        sys.exit(1)

    print(f"Fusion de {len(fichiers)} fichier(s) :")
    for f in fichiers:
        print(f"  {f}")

    resultats = [charger_json(f) for f in fichiers]
    fusionne = fusionner(resultats)

    if not fusionne['tailles']:
        print("Aucune taille complète après fusion. Vérifiez vos fichiers.")
        sys.exit(1)

    print("\nRépétitions disponibles par taille :")
    for t in fusionne['tailles']:
        n = len(fusionne['theta_NO'][t])
        print(f"  n={t:6d} : {n} rép.")

    afficher_resultats(fusionne)
