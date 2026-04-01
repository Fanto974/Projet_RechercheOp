import os
from problem import Problem
from readAndDisplayFunc import lire_fichier

choice = -1
nbProb = 12
dossier = "files"

while choice != 0:
    try:
        choice = int(input(f"Quel probleme de transport voulez-vous analyser ?\n1 : Entrez un nombre entre 1 et {nbProb}\n0 : Quitter"))
        if choice < 0 or choice > 12:
            print("Numéro invalide.")
            continue
    except ValueError:
        print("Entrée invalide.")
        continue
    if choice == 0:
        break

    chemin = os.path.join(dossier, f"1-5-{choice}.txt")
    p = Problem(chemin)
    if not p.check_validity():
        continue

    # Afficher la matrice des coûts
    p.repr_prob()


    # --- Initialisation ---
    methode = -1
    while methode != 0:
        try:
            methode = int(input(
                f"Quel méthode d'initialisation vouslez-vous utiliser ?\n1 : Nord Ouest\n2 : Balas-Hammer\n0 : Revenir au choix du problème"))
            if methode < 0 or methode > 12:
                print("Numéro invalide.")
                continue
        except ValueError:
            print("Entrée invalide.")
            continue
        if choice == 0:
            break

        if methode == 1:
            print("\n--- Méthode Nord Ouest ---")
            p.nord_ouest()
        if methode == 2:
            print("\n--- Méthode Balas-Hammer ---")
            p.balas_hammer()
        p.repr_prop()
        p.cout_total()
        print(f"  Coût de la proposition initiale = {p.coutProp}")


        # --- Marche Pied ---
        print("\n--- Méthode du marche-pied avec potentiel ---")
        p.methode_marche_pied()





