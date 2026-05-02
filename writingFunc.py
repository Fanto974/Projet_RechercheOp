"""Module indépendant de de génération des traces et exécution pour les fichiers de tests."""
import os


def executer_et_sauvegarder_trace(num_probleme, methode, groupe="1", equipe="5",
                                  dossier_problemes="files", dossier_traces="traces"):
    """
    Exécute un problème avec la méthode choisie et sauvegarde la trace dans un fichier .txt.

    Paramètres :
        num_probleme (int) : numéro du problème (1-12)
        methode (str) : "no" pour Nord-Ouest, "bh" pour Balas-Hammer
        groupe, equipe (str) : identifiants pour le nom du fichier
        dossier_problemes (str) : dossier contenant les fichiers .txt des problèmes
        dossier_traces (str) : dossier où sauvegarder les traces
    """
    import contextlib
    from problem import Problem

    if not os.path.exists(dossier_traces):
        os.makedirs(dossier_traces)

    nom_fichier = f"{groupe}-{equipe}-trace{num_probleme}-{methode}.txt"
    chemin_trace = os.path.join(dossier_traces, nom_fichier)
    chemin_probleme = os.path.join(dossier_problemes, f"1-5-{num_probleme}.txt")

    with open(chemin_trace, 'w', encoding='utf-8') as f:
        with contextlib.redirect_stdout(f):
            p = Problem(chemin_probleme)
            if not p.check_validity():
                return
            p.repr_prob()

            if methode == "no":
                print("\n--- Méthode Nord-Ouest ---")
                p.nord_ouest()
                p.repr_prop("PROPOSITION INITIALE (Nord-Ouest)")
            else:
                print("\n--- Méthode Balas-Hammer ---")
                p.balas_hammer()
                p.repr_prop("PROPOSITION INITIALE (Balas-Hammer)")

            p.cout_total()
            print(f"  Coût de la proposition initiale = {p.coutProp}")
            p.methode_marche_pied()

    print(f"Trace sauvegardée : {chemin_trace}")


def generer_toutes_les_traces(groupe="1", equipe="5"):
    """Génère les 24 traces d'exécution (12 problèmes x 2 méthodes)."""
    from createFiles import creer_tous_les_fichiers
    creer_tous_les_fichiers()

    for num in range(1, 13):
        for methode in ["no", "bh"]:
            print(f"Exécution problème {num} - {methode.upper()}...")
            executer_et_sauvegarder_trace(num, methode, groupe=groupe, equipe=equipe)

if __name__ == "__main__":
    generer_toutes_les_traces(groupe="1", equipe="5")