"""
=============================================================================
PROJET DE RECHERCHE OPÉRATIONNELLE - PROBLÈME DE TRANSPORT
Efrei Paris - Semestre de printemps 25/26 - S6
=============================================================================

Ce programme résout des problèmes de transport équilibrés en utilisant :
- La méthode Nord-Ouest pour la proposition initiale
- La méthode Balas-Hammer pour la proposition initiale
- La méthode du marche-pied avec potentiel pour l'optimisation

Auteur : [Votre nom]
"""

import os
import sys
import time
import random
import math
from collections import deque
from copy import deepcopy

# =============================================================================
# ÉTAPE 1 : LECTURE DES DONNÉES DEPUIS UN FICHIER .TXT
# =============================================================================
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

def lire_fichier(chemin):
    """
    Lit un fichier .txt contenant un problème de transport.
    
    Paramètres :
        chemin (str) : chemin vers le fichier .txt
    
    Retourne :
        n (int) : nombre de fournisseurs
        m (int) : nombre de clients
        couts (list[list[int]]) : matrice des coûts unitaires (n x m)
        provisions (list[int]) : provisions de chaque fournisseur
        commandes (list[int]) : commandes de chaque client
    """
    with open(chemin, 'r') as f:
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


# =============================================================================
# ÉTAPE 2 : FONCTIONS D'AFFICHAGE
# =============================================================================
# L'affichage doit être soigné : colonnes bien alignées, pas de décalage.
#
# On affiche :
#   - La matrice des coûts
#   - La proposition de transport (matrice B)
#   - La table des coûts potentiels
#   - La table des coûts marginaux
#
# Pseudo-code pour chaque affichage :
#   Calculer la largeur maximale de chaque colonne
#   Afficher l'en-tête avec les noms de colonnes
#   Pour chaque ligne :
#       Afficher le nom de la ligne + les valeurs alignées

def largeur_col(matrice, provisions, commandes, m, en_tete_ligne="P"):
    """Calcule la largeur nécessaire pour chaque colonne."""
    # Largeur pour les noms de lignes (P1, P2, etc.)
    larg_nom = max(len(f"{en_tete_ligne}{i+1}") for i in range(len(matrice))) + 1
    larg_nom = max(larg_nom, len("Commandes") + 1)
    
    # Largeur pour chaque colonne de données
    largeurs = []
    for j in range(m):
        w = len(f"C{j+1}")
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


def afficher_matrice_couts(couts, provisions, commandes, n, m):
    """
    Affiche la matrice des coûts unitaires de transport.
    
    Format :
              C1    C2    ...   Cm    Provisions
    P1        a11   a12   ...   a1m   P1
    ...
    Pn        an1   an2   ...   anm   Pn
    Commandes C1    C2    ...   Cm
    """
    print("\n" + "=" * 60)
    print("  MATRICE DES COÛTS UNITAIRES")
    print("=" * 60)
    
    larg_nom, largeurs, larg_prov = largeur_col(couts, provisions, commandes, m)
    
    # En-tête
    en_tete = " " * larg_nom
    for j in range(m):
        en_tete += f"{'C' + str(j+1):>{largeurs[j]}}"
    en_tete += f"{'Provisions':>{larg_prov}}"
    print(en_tete)
    print("-" * len(en_tete))
    
    # Lignes des fournisseurs
    for i in range(n):
        ligne = f"{'P' + str(i+1):<{larg_nom}}"
        for j in range(m):
            ligne += f"{couts[i][j]:>{largeurs[j]}}"
        ligne += f"{provisions[i]:>{larg_prov}}"
        print(ligne)
    
    # Ligne des commandes
    print("-" * len(en_tete))
    ligne_cmd = f"{'Commandes':<{larg_nom}}"
    for j in range(m):
        ligne_cmd += f"{commandes[j]:>{largeurs[j]}}"
    print(ligne_cmd)
    print()


def afficher_proposition(proposition, provisions, commandes, n, m, titre="PROPOSITION DE TRANSPORT"):
    """
    Affiche la proposition de transport (matrice B).
    Les cases à None ou -1 sont affichées comme '.' (non utilisées).
    """
    print("\n" + "=" * 60)
    print(f"  {titre}")
    print("=" * 60)
    
    # Préparer une matrice affichable
    mat_aff = []
    for i in range(n):
        ligne = []
        for j in range(m):
            val = proposition[i][j]
            if val is None or val == -1:
                ligne.append("0")
            else:
                ligne.append(str(val))
        mat_aff.append(ligne)
    
    # Calculer les largeurs
    larg_nom = max(len(f"P{i+1}") for i in range(n)) + 1
    larg_nom = max(larg_nom, len("Commandes") + 1)
    
    largeurs = []
    for j in range(m):
        w = len(f"C{j+1}")
        for i in range(n):
            w = max(w, len(mat_aff[i][j]))
        w = max(w, len(str(commandes[j])))
        largeurs.append(w + 2)
    
    larg_prov = len("Provisions")
    for p in provisions:
        larg_prov = max(larg_prov, len(str(p)))
    larg_prov += 2
    
    # En-tête
    en_tete = " " * larg_nom
    for j in range(m):
        en_tete += f"{'C' + str(j+1):>{largeurs[j]}}"
    en_tete += f"{'Provisions':>{larg_prov}}"
    print(en_tete)
    print("-" * len(en_tete))
    
    # Lignes
    for i in range(n):
        ligne = f"{'P' + str(i+1):<{larg_nom}}"
        for j in range(m):
            ligne += f"{mat_aff[i][j]:>{largeurs[j]}}"
        ligne += f"{provisions[i]:>{larg_prov}}"
        print(ligne)
    
    # Commandes
    print("-" * len(en_tete))
    ligne_cmd = f"{'Commandes':<{larg_nom}}"
    for j in range(m):
        ligne_cmd += f"{commandes[j]:>{largeurs[j]}}"
    print(ligne_cmd)
    print()


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
    larg_nom = max(len(f"P{i+1}") for i in range(n)) + 1
    largeurs = []
    for j in range(m):
        w = len(f"C{j+1}")
        for i in range(n):
            val = potentiels_u[i] + potentiels_v[j]
            w = max(w, len(str(val)))
        largeurs.append(w + 2)
    
    en_tete = " " * larg_nom
    for j in range(m):
        en_tete += f"{'C' + str(j+1):>{largeurs[j]}}"
    print(en_tete)
    print("-" * len(en_tete))
    
    for i in range(n):
        ligne = f"{'P' + str(i+1):<{larg_nom}}"
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
        w = len(f"C{j+1}")
        for i in range(n):
            if proposition[i][j] is not None and proposition[i][j] != -1:
                w = max(w, 1)  # Pour "0" ou "*"
            else:
                w = max(w, len(str(marginaux[i][j])))
        largeurs_m.append(w + 2)
    
    en_tete = " " * larg_nom
    for j in range(m):
        en_tete += f"{'C' + str(j+1):>{largeurs_m[j]}}"
    print(en_tete)
    print("-" * len(en_tete))
    
    meilleure_arete = None
    meilleur_marginal = 0
    
    for i in range(n):
        ligne = f"{'P' + str(i+1):<{larg_nom}}"
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


# =============================================================================
# ÉTAPE 3 : ALGORITHME NORD-OUEST
# =============================================================================
# Principe : on parcourt la matrice de haut-gauche (nord-ouest) vers bas-droite.
# À chaque étape, on remplit la case (i, j) avec le minimum entre la provision
# restante du fournisseur i et la commande restante du client j.
#
# Pseudo-code :
#   i = 0, j = 0
#   prov = copie(provisions), cmd = copie(commandes)
#   Tant que i < n et j < m :
#       quantite = min(prov[i], cmd[j])
#       B[i][j] = quantite
#       prov[i] -= quantite
#       cmd[j] -= quantite
#       Si prov[i] == 0 : i += 1
#       Si cmd[j] == 0  : j += 1

def nord_ouest(couts, provisions, commandes, n, m):
    """
    Calcule la proposition initiale par la méthode Nord-Ouest.
    
    Retourne :
        proposition (list[list]) : matrice n x m, None = hors-base, valeur = en base
    """
    proposition = [[None] * m for _ in range(n)]
    prov = provisions[:]
    cmd = commandes[:]
    
    i, j = 0, 0
    
    print("\n--- Déroulement de Nord-Ouest ---")
    
    while i < n and j < m:
        quantite = min(prov[i], cmd[j])
        proposition[i][j] = quantite
        print(f"  Case ({i+1},{j+1}) : min(prov={prov[i]}, cmd={cmd[j]}) = {quantite}")
        
        prov[i] -= quantite
        cmd[j] -= quantite
        
        if prov[i] == 0 and cmd[j] == 0:
            # Les deux sont épuisés : on avance en diagonale
            # Cas de dégénérescence possible
            i += 1
            j += 1
        elif prov[i] == 0:
            i += 1
        else:
            j += 1
    
    return proposition


# =============================================================================
# ÉTAPE 4 : ALGORITHME BALAS-HAMMER
# =============================================================================
# Principe : à chaque étape, on calcule la "pénalité" de chaque ligne et colonne.
# La pénalité est la différence entre les deux plus petits coûts non barrés.
# On choisit la ligne ou colonne de pénalité maximale, puis on affecte le maximum
# possible à la case de coût minimum dans cette ligne/colonne.
#
# Pseudo-code :
#   Tant qu'il reste des lignes et colonnes actives :
#       Pour chaque ligne active : pénalité = 2e_min - 1er_min des coûts non barrés
#       Pour chaque colonne active : idem
#       Sélectionner la ligne ou colonne de pénalité maximale
#       Dans cette ligne/colonne, trouver la case de coût minimum
#       Affecter min(prov[i], cmd[j]) à cette case
#       Mettre à jour provisions et commandes
#       Barrer la ligne ou colonne épuisée

def balas_hammer(couts, provisions, commandes, n, m):
    """
    Calcule la proposition initiale par la méthode Balas-Hammer.
    
    Retourne :
        proposition (list[list]) : matrice n x m
    """
    proposition = [[None] * m for _ in range(n)]
    prov = provisions[:]
    cmd = commandes[:]
    
    lignes_actives = set(range(n))
    colonnes_actives = set(range(m))
    
    print("\n--- Déroulement de Balas-Hammer ---")
    etape = 0
    
    while lignes_actives and colonnes_actives:
        etape += 1
        print(f"\n  Étape {etape} :")
        
        # Calculer les pénalités des lignes
        penalites_lignes = {}
        for i in lignes_actives:
            couts_actifs = []
            for j in colonnes_actives:
                couts_actifs.append((couts[i][j], j))
            couts_actifs.sort()
            if len(couts_actifs) >= 2:
                penalites_lignes[i] = couts_actifs[1][0] - couts_actifs[0][0]
            elif len(couts_actifs) == 1:
                penalites_lignes[i] = couts_actifs[0][0]
            else:
                penalites_lignes[i] = 0
        
        # Calculer les pénalités des colonnes
        penalites_colonnes = {}
        for j in colonnes_actives:
            couts_actifs = []
            for i in lignes_actives:
                couts_actifs.append((couts[i][j], i))
            couts_actifs.sort()
            if len(couts_actifs) >= 2:
                penalites_colonnes[j] = couts_actifs[1][0] - couts_actifs[0][0]
            elif len(couts_actifs) == 1:
                penalites_colonnes[j] = couts_actifs[0][0]
            else:
                penalites_colonnes[j] = 0
        
        # Afficher les pénalités
        print("    Pénalités lignes  :", {f"P{i+1}": penalites_lignes[i] for i in sorted(penalites_lignes)})
        print("    Pénalités colonnes:", {f"C{j+1}": penalites_colonnes[j] for j in sorted(penalites_colonnes)})
        
        # Trouver la pénalité maximale
        max_pen_ligne = max(penalites_lignes.values()) if penalites_lignes else -1
        max_pen_col = max(penalites_colonnes.values()) if penalites_colonnes else -1
        
        if max_pen_ligne >= max_pen_col:
            # Choisir parmi les lignes de pénalité max
            lignes_max = [i for i in penalites_lignes if penalites_lignes[i] == max_pen_ligne]
            print(f"    Pénalité max = {max_pen_ligne} sur ligne(s) : {['P'+str(i+1) for i in lignes_max]}")
            
            # Prendre la première ligne de pénalité max
            i_choisi = lignes_max[0]
            
            # Trouver le coût minimum dans cette ligne parmi les colonnes actives
            min_cout = float('inf')
            j_choisi = None
            for j in colonnes_actives:
                if couts[i_choisi][j] < min_cout:
                    min_cout = couts[i_choisi][j]
                    j_choisi = j
        else:
            # Choisir parmi les colonnes de pénalité max
            colonnes_max = [j for j in penalites_colonnes if penalites_colonnes[j] == max_pen_col]
            print(f"    Pénalité max = {max_pen_col} sur colonne(s) : {['C'+str(j+1) for j in colonnes_max]}")
            
            j_choisi = colonnes_max[0]
            
            # Trouver le coût minimum dans cette colonne parmi les lignes actives
            min_cout = float('inf')
            i_choisi = None
            for i in lignes_actives:
                if couts[i][j_choisi] < min_cout:
                    min_cout = couts[i][j_choisi]
                    i_choisi = i
        
        # Affecter la quantité
        quantite = min(prov[i_choisi], cmd[j_choisi])
        proposition[i_choisi][j_choisi] = quantite
        print(f"    -> Affectation case ({i_choisi+1},{j_choisi+1}) : coût={min_cout}, quantité={quantite}")
        
        prov[i_choisi] -= quantite
        cmd[j_choisi] -= quantite
        
        # Barrer ligne ou colonne épuisée
        if prov[i_choisi] == 0 and cmd[j_choisi] == 0:
            # Dégénérescence : on barre la ligne et on garde la colonne
            lignes_actives.discard(i_choisi)
            colonnes_actives.discard(j_choisi)
            print(f"    Ligne P{i_choisi+1} ET Colonne C{j_choisi+1} épuisées")
        elif prov[i_choisi] == 0:
            lignes_actives.discard(i_choisi)
            print(f"    Ligne P{i_choisi+1} épuisée")
        else:
            colonnes_actives.discard(j_choisi)
            print(f"    Colonne C{j_choisi+1} épuisée")
    
    return proposition


# =============================================================================
# ÉTAPE 5 : CALCUL DU COÛT TOTAL
# =============================================================================
# Le coût total est la somme de a_ij * b_ij pour toutes les cases de base.
#
# Pseudo-code :
#   cout_total = 0
#   Pour chaque (i,j) :
#       Si B[i][j] est en base :
#           cout_total += a[i][j] * B[i][j]

def cout_total(couts, proposition, n, m):
    """
    Calcule le coût total d'une proposition de transport.
    """
    total = 0
    for i in range(n):
        for j in range(m):
            if proposition[i][j] is not None and proposition[i][j] != -1:
                total += couts[i][j] * proposition[i][j]
    return total


# =============================================================================
# ÉTAPE 6 : MÉTHODE DU MARCHE-PIED AVEC POTENTIEL
# =============================================================================

# --- 6.1 : Construction du graphe biparti à partir de la proposition ---
# Le graphe biparti a n sommets "fournisseurs" et m sommets "clients".
# Une arête (i, j) existe si B[i][j] est en base (non None et non -1).

def aretes_base(proposition, n, m):
    """Retourne la liste des arêtes de base (i, j)."""
    aretes = []
    for i in range(n):
        for j in range(m):
            if proposition[i][j] is not None and proposition[i][j] != -1:
                aretes.append((i, j))
    return aretes


# --- 6.2 : Test d'acyclicité par parcours en largeur (BFS) ---
# On construit un graphe non orienté biparti :
#   - Sommets fournisseurs : indices 0 à n-1
#   - Sommets clients : indices n à n+m-1
# On fait un BFS. Si on tombe sur un sommet déjà visité qui n'est pas le parent,
# alors il y a un cycle.
#
# Pseudo-code :
#   Construire la liste d'adjacence du graphe biparti
#   BFS depuis un sommet de départ
#   Si on visite un sommet déjà visité et != parent : cycle détecté
#   Reconstruire le cycle en remontant les parents

def construire_adjacence(aretes, n, m):
    """
    Construit la liste d'adjacence du graphe biparti sous forme de DICTIONNAIRE.
    
    Chaque clé est un sommet (identifié par une chaîne) :
        - "P0", "P1", ... pour les fournisseurs
        - "C0", "C1", ... pour les clients
    Chaque valeur est une liste de sommets voisins.
    
    Avantage du dictionnaire vs liste de listes :
        - On ne crée des entrées que pour les sommets qui ont des voisins
          (pas de cases vides pour les sommets isolés)
        - Les clés sont explicites ("P2", "C0") au lieu d'indices numériques
          arbitraires, ce qui rend le code plus lisible et le débogage plus facile
        - On n'a pas besoin de connaître n+m à l'avance pour dimensionner la structure
    
    Exemple avec aretes = [(0,1), (1,0), (1,1)] et n=2, m=2 :
        {
            "P0": ["C1"],
            "C1": ["P0", "P1"],
            "P1": ["C0", "C1"],
            "C0": ["P1"]
        }
    """
    adj = {}
    for (i, j) in aretes:
        cle_fournisseur = f"P{i}"   # Sommet fournisseur
        cle_client = f"C{j}"        # Sommet client
        
        # Ajouter le client dans les voisins du fournisseur
        if cle_fournisseur not in adj:
            adj[cle_fournisseur] = []
        adj[cle_fournisseur].append(cle_client)
        
        # Ajouter le fournisseur dans les voisins du client (graphe non orienté)
        if cle_client not in adj:
            adj[cle_client] = []
        adj[cle_client].append(cle_fournisseur)
    
    return adj


def detecter_cycle_bfs(aretes, n, m):
    """
    Détecte un cycle dans le graphe biparti par BFS.
    Utilise un dictionnaire pour la liste d'adjacence.
    
    Retourne :
        (has_cycle, cycle_aretes)
        has_cycle (bool) : True si un cycle est détecté
        cycle_aretes (list) : liste des arêtes (i,j) formant le cycle
                              (indices fournisseur/client numériques)
    """
    if not aretes:
        return False, []
    
    adj = construire_adjacence(aretes, n, m)
    
    # Dictionnaires pour le BFS (au lieu de listes indexées par entier)
    visite = {}    # sommet -> True/False
    parent = {}    # sommet -> sommet parent (ou None pour la racine)
    
    # Initialiser tous les sommets comme non visités
    for sommet in adj:
        visite[sommet] = False
        parent[sommet] = None
    
    # Parcourir toutes les composantes connexes
    for depart in adj:
        if visite[depart]:
            continue
        
        file = deque([depart])
        visite[depart] = True
        
        while file:
            u = file.popleft()
            
            for v in adj.get(u, []):
                if not visite[v]:
                    # Sommet non encore visité : on le découvre
                    visite[v] = True
                    parent[v] = u
                    file.append(v)
                    
                elif v != parent[u]:
                    # Sommet déjà visité et ce n'est pas le parent
                    # => CYCLE DÉTECTÉ entre u et v
                    print(f"  Cycle détecté entre sommets {u} et {v}")
                    
                    # --- Reconstruction du cycle ---
                    
                    # 1) Collecter les ancêtres de u
                    ancetres_u = set()
                    x = u
                    while x is not None:
                        ancetres_u.add(x)
                        x = parent[x]
                    
                    # 2) Remonter depuis v jusqu'à trouver l'ancêtre commun
                    chemin_v = []
                    y = v
                    while y not in ancetres_u:
                        chemin_v.append(y)
                        y = parent[y]
                    ancetre_commun = y
                    chemin_v.append(ancetre_commun)
                    
                    # 3) Remonter depuis u jusqu'à l'ancêtre commun
                    chemin_u = []
                    x = u
                    while x != ancetre_commun:
                        chemin_u.append(x)
                        x = parent[x]
                    chemin_u.append(ancetre_commun)
                    
                    # 4) Assembler le cycle : u -> ancêtre -> v
                    cycle_sommets = chemin_u + chemin_v[::-1][1:]
                    
                    # 5) Convertir les sommets ("P0", "C1", ...) en arêtes (i, j)
                    cycle_aretes = []
                    for k in range(len(cycle_sommets)):
                        s1 = cycle_sommets[k]
                        s2 = cycle_sommets[(k + 1) % len(cycle_sommets)]
                        
                        # Identifier qui est le fournisseur et qui est le client
                        if s1.startswith("P") and s2.startswith("C"):
                            i = int(s1[1:])
                            j = int(s2[1:])
                            cycle_aretes.append((i, j))
                        elif s1.startswith("C") and s2.startswith("P"):
                            j = int(s1[1:])
                            i = int(s2[1:])
                            cycle_aretes.append((i, j))
                    
                    print(f"  Cycle (arêtes) : {[(i+1,j+1) for (i,j) in cycle_aretes]}")
                    return True, cycle_aretes
    
    return False, []


# --- 6.3 : Maximisation du transport sur un cycle ---
# Quand on ajoute une arête améliorante, un cycle se forme.
# On alterne les signes + et - sur le cycle.
# delta = min des valeurs sur les arêtes marquées -.
# On ajoute delta aux + et soustrait delta aux -.
# On supprime l'arête qui tombe à 0.
#
# Pseudo-code :
#   Identifier les arêtes + et - du cycle
#   delta = min(B[i][j] pour arêtes -)
#   Pour chaque arête du cycle :
#       Si + : B[i][j] += delta
#       Si - : B[i][j] -= delta
#   Supprimer les arêtes à 0

def trouver_cycle_avec_arete(proposition, n, m, arete_ajoutee):
    """
    Trouve le cycle formé par l'ajout de arete_ajoutee à la proposition.
    
    Le cycle dans un tableau de transport est une séquence de cases
    (i0,j0), (i0,j1), (i1,j1), (i1,j2), ..., (ik,j0)
    où les cases consécutives partagent alternativement une ligne ou une colonne.
    Le cycle a un nombre PAIR d'éléments.
    
    On utilise un DFS sur les cases. Depuis (i,j) :
      - Si la dernière transition était un changement de colonne (même ligne),
        la prochaine doit être un changement de ligne (même colonne).
      - Et vice versa.
    
    Retourne :
        cycle (list of (i, j)) : liste ordonnée des cases du cycle.
              La première case est l'arête ajoutée (qui sera +).
    """
    i_add, j_add = arete_ajoutee
    
    # Collecter les cases de base
    base = set()
    for i in range(n):
        for j in range(m):
            if proposition[i][j] is not None and proposition[i][j] != -1:
                base.add((i, j))
    
    # Toutes les cases (base + ajoutée)
    toutes = base | {(i_add, j_add)}
    
    # Construire les adjacences
    par_ligne = {}   # ligne i -> ensemble des colonnes j
    par_colonne = {} # colonne j -> ensemble des lignes i
    for (i, j) in toutes:
        par_ligne.setdefault(i, set()).add(j)
        par_colonne.setdefault(j, set()).add(i)
    
    # DFS : on part de (i_add, j_add)
    # À chaque pas, on alterne entre :
    #   - "chercher sur la même ligne" (changer de colonne) 
    #   - "chercher sur la même colonne" (changer de ligne)
    # On commence par chercher sur la même colonne (changer de ligne)
    
    def dfs(chemin, visite_cases, cherche_sur_colonne):
        """
        cherche_sur_colonne : si True, depuis la dernière case (i, j),
            on cherche un i' != i tel que (i', j) est dans 'toutes'.
            La prochaine étape sera (i', j) et on cherchera sur la ligne.
            si False, depuis (i, j), on cherche j' != j tel que (i, j') 
            est dans 'toutes'.
        """
        i_cur, j_cur = chemin[-1]
        
        if cherche_sur_colonne:
            # Chercher un autre fournisseur sur la colonne j_cur
            for i_next in par_colonne.get(j_cur, set()):
                if i_next == i_cur:
                    continue
                case = (i_next, j_cur)
                # Peut-on fermer le cycle?
                if case == (i_add, j_add) and len(chemin) >= 4 and len(chemin) % 2 == 0:
                    return True
                if case in visite_cases:
                    continue
                chemin.append(case)
                visite_cases.add(case)
                if dfs(chemin, visite_cases, False):  # prochain: chercher sur ligne
                    return True
                visite_cases.discard(case)
                chemin.pop()
        else:
            # Chercher un autre client sur la ligne i_cur
            for j_next in par_ligne.get(i_cur, set()):
                if j_next == j_cur:
                    continue
                case = (i_cur, j_next)
                # Peut-on fermer le cycle?
                if case == (i_add, j_add) and len(chemin) >= 4 and len(chemin) % 2 == 0:
                    return True
                if case in visite_cases:
                    continue
                chemin.append(case)
                visite_cases.add(case)
                if dfs(chemin, visite_cases, True):  # prochain: chercher sur colonne
                    return True
                visite_cases.discard(case)
                chemin.pop()
        return False
    
    # Essai 1 : depuis (i_add, j_add), chercher d'abord sur la colonne
    chemin = [(i_add, j_add)]
    visite = {(i_add, j_add)}
    if dfs(chemin, visite, True):
        return chemin
    
    # Essai 2 : depuis (i_add, j_add), chercher d'abord sur la ligne
    chemin = [(i_add, j_add)]
    visite = {(i_add, j_add)}
    if dfs(chemin, visite, False):
        return chemin
    
    print("  ERREUR : Cycle non trouvé !")
    return []


def maximiser_transport_cycle(proposition, cycle, n, m):
    """
    Maximise le transport sur un cycle.
    
    Le cycle est alternativement + et - :
    - La première arête (l'arête ajoutée) est +
    - Les suivantes alternent -, +, -, +, ...
    
    delta = min des valeurs sur les arêtes -
    
    Retourne :
        proposition modifiée
        delta (int) : la quantité transférée
        aretes_supprimees (list) : arêtes tombées à 0
    """
    if not cycle:
        return proposition, 0, []
    
    # Identifier les arêtes + et -
    aretes_plus = []
    aretes_moins = []
    for k, (i, j) in enumerate(cycle):
        if k % 2 == 0:
            aretes_plus.append((i, j))
        else:
            aretes_moins.append((i, j))
    
    print("  Arêtes + :", [(i+1, j+1) for (i, j) in aretes_plus])
    print("  Arêtes - :", [(i+1, j+1) for (i, j) in aretes_moins])
    
    # Calculer delta
    delta = float('inf')
    for (i, j) in aretes_moins:
        val = proposition[i][j]
        if val is not None and val != -1:
            delta = min(delta, val)
        else:
            delta = 0
    
    print(f"  delta = {delta}")
    
    # Appliquer le transfert
    for (i, j) in aretes_plus:
        if proposition[i][j] is None or proposition[i][j] == -1:
            proposition[i][j] = delta
        else:
            proposition[i][j] += delta
    
    aretes_supprimees = []
    for (i, j) in aretes_moins:
        proposition[i][j] -= delta
        if proposition[i][j] == 0:
            aretes_supprimees.append((i, j))
    
    # Supprimer UNE arête à 0 (la première trouvée dans les arêtes -)
    if aretes_supprimees:
        # On supprime la dernière arête à 0 dans les arêtes -
        i_sup, j_sup = aretes_supprimees[-1]
        proposition[i_sup][j_sup] = None
        print(f"  Arête supprimée : ({i_sup+1}, {j_sup+1})")
        
        # S'il y a d'autres arêtes à 0, on les garde à 0 (dégénérescence)
        if len(aretes_supprimees) > 1:
            print(f"  Attention : dégénérescence, arêtes restantes à 0 : "
                  f"{[(i+1,j+1) for (i,j) in aretes_supprimees[:-1]]}")
    
    return proposition, delta, aretes_supprimees


# --- 6.4 : Test de connexité par BFS ---
# On vérifie que le graphe biparti des arêtes de base est connexe.
# S'il ne l'est pas, on identifie les composantes connexes.
#
# Pseudo-code :
#   BFS depuis un sommet quelconque de la base
#   Si tous les sommets touchés par la base sont visités : connexe
#   Sinon : identifier les composantes connexes

def test_connexite_bfs(aretes, n, m):
    """
    Teste si le graphe biparti formé par les arêtes de base est connexe.
    Utilise un dictionnaire pour la liste d'adjacence.
    
    Retourne :
        (est_connexe, composantes)
        est_connexe (bool)
        composantes (list of list) : chaque composante est une liste de sommets
                                     (clés de type "P0", "C1", etc.)
    """
    if not aretes:
        return False, []
    
    adj = construire_adjacence(aretes, n, m)
    
    # Dictionnaire pour marquer les sommets visités
    visite = {sommet: False for sommet in adj}
    
    composantes = []
    
    for depart in adj:
        if visite[depart]:
            continue
        
        composante = []
        file = deque([depart])
        visite[depart] = True
        
        while file:
            u = file.popleft()
            composante.append(u)
            for v in adj.get(u, []):
                if not visite.get(v, True):  # True par défaut = considéré comme visité
                    visite[v] = True
                    file.append(v)
        
        composantes.append(composante)
    
    est_connexe = len(composantes) == 1
    
    if not est_connexe:
        print(f"  Graphe NON connexe : {len(composantes)} composantes")
        for k, comp in enumerate(composantes):
            # Extraire les fournisseurs ("P0" -> 1) et clients ("C0" -> 1)
            fournisseurs = [int(s[1:]) + 1 for s in comp if s.startswith("P")]
            clients = [int(s[1:]) + 1 for s in comp if s.startswith("C")]
            print(f"    Composante {k+1} : Fournisseurs {fournisseurs}, Clients {clients}")
    else:
        print("  Graphe connexe : OK")
    
    return est_connexe, composantes


def rendre_connexe(proposition, couts, aretes, n, m, composantes):
    """
    Rend le graphe connexe en ajoutant des arêtes de coût minimum
    entre les composantes.
    Les arêtes ajoutées ont une valeur de 0 (dégénérescence).
    On trie les arêtes hors-base par coût croissant et on ajoute
    celles qui relient deux composantes différentes.
    
    Les composantes contiennent des clés "P0", "C1", etc. (format dictionnaire).
    """
    # Créer un dictionnaire sommet -> numéro de composante
    comp_de = {}
    for k, comp in enumerate(composantes):
        for s in comp:
            comp_de[s] = k
    
    # Lister toutes les arêtes hors-base triées par coût croissant
    aretes_hors_base = []
    for i in range(n):
        for j in range(m):
            if proposition[i][j] is None or proposition[i][j] == -1:
                aretes_hors_base.append((couts[i][j], i, j))
    aretes_hors_base.sort()
    
    nb_composantes = len(composantes)
    
    for (cout, i, j) in aretes_hors_base:
        cle_f = f"P{i}"    # Clé du fournisseur dans le dictionnaire
        cle_c = f"C{j}"    # Clé du client dans le dictionnaire
        
        if cle_f in comp_de and cle_c in comp_de:
            if comp_de[cle_f] != comp_de[cle_c]:
                # Cette arête relie deux composantes -> l'ajouter
                proposition[i][j] = 0
                print(f"  Ajout arête ({i+1},{j+1}) avec coût {cout} pour relier les composantes")
                
                # Fusionner les composantes
                ancien = comp_de[cle_c]
                nouveau = comp_de[cle_f]
                for s in comp_de:
                    if comp_de[s] == ancien:
                        comp_de[s] = nouveau
                
                nb_composantes -= 1
                if nb_composantes == 1:
                    break
        elif cle_f not in comp_de:
            proposition[i][j] = 0
            if cle_c in comp_de:
                comp_de[cle_f] = comp_de[cle_c]
            print(f"  Ajout arête ({i+1},{j+1}) pour intégrer P{i+1}")
        elif cle_c not in comp_de:
            proposition[i][j] = 0
            if cle_f in comp_de:
                comp_de[cle_c] = comp_de[cle_f]
            print(f"  Ajout arête ({i+1},{j+1}) pour intégrer C{j+1}")
    
    return proposition


# --- 6.5 : Calcul des potentiels ---
# Pour un arbre couvrant (proposition non dégénérée), on a :
# u_i + v_j = a_ij pour chaque arête de base (i, j)
# On fixe u_0 = 0 et on calcule les autres par propagation BFS.
#
# Pseudo-code :
#   u[0] = 0
#   BFS sur l'arbre des arêtes de base
#   Pour chaque arête (i, j) visitée :
#       Si u[i] est connu : v[j] = a[i][j] - u[i]
#       Si v[j] est connu : u[i] = a[i][j] - v[j]

def calculer_potentiels(couts, proposition, n, m):
    """
    Calcule les potentiels u_i et v_j tels que u_i + v_j = a_ij
    pour chaque arête de base.
    
    Retourne :
        u (list) : potentiels des fournisseurs
        v (list) : potentiels des clients
    """
    u = [None] * n
    v = [None] * m
    
    # Construire les adjacences
    adj_fournisseur = [[] for _ in range(n)]  # Pour chaque fournisseur, liste des clients en base
    adj_client = [[] for _ in range(m)]  # Pour chaque client, liste des fournisseurs en base
    
    for i in range(n):
        for j in range(m):
            if proposition[i][j] is not None and proposition[i][j] != -1:
                adj_fournisseur[i].append(j)
                adj_client[j].append(i)
    
    # Fixer u[0] = 0
    u[0] = 0
    
    # BFS pour propager les potentiels
    file = deque()
    file.append(('u', 0))  # On commence par le fournisseur 0
    
    while file:
        type_sommet, idx = file.popleft()
        
        if type_sommet == 'u':
            # Fournisseur idx : u[idx] est connu
            for j in adj_fournisseur[idx]:
                if v[j] is None:
                    v[j] = couts[idx][j] - u[idx]
                    file.append(('v', j))
        else:
            # Client idx : v[idx] est connu
            for i in adj_client[idx]:
                if u[i] is None:
                    u[i] = couts[i][idx] - v[idx]
                    file.append(('u', i))
    
    return u, v


# --- 6.6 : Vérification de la non-dégénérescence ---
# Une proposition non dégénérée a exactement n + m - 1 arêtes de base.

def est_non_degeneree(proposition, n, m):
    """Vérifie que la proposition a exactement n + m - 1 arêtes de base."""
    nb_aretes = sum(1 for i in range(n) for j in range(m) 
                    if proposition[i][j] is not None and proposition[i][j] != -1)
    attendu = n + m - 1
    print(f"  Nombre d'arêtes de base : {nb_aretes} (attendu : {attendu})")
    return nb_aretes == attendu


# =============================================================================
# ÉTAPE 7 : BOUCLE PRINCIPALE DU MARCHE-PIED AVEC POTENTIEL
# =============================================================================
# Pseudo-code global :
#   Tant que la proposition n'est pas optimale :
#     1. Vérifier la non-dégénérescence
#     2. Si cycle : maximiser et supprimer
#     3. Si non connexe : ajouter des arêtes
#     4. Calculer les potentiels
#     5. Calculer les coûts marginaux
#     6. Trouver l'arête améliorante (marginal le plus négatif)
#     7. Si pas d'arête améliorante : OPTIMAL
#     8. Sinon : ajouter l'arête, trouver le cycle, maximiser

def methode_marche_pied(couts, proposition, provisions, commandes, n, m):
    """
    Résout le problème de transport par la méthode du marche-pied avec potentiel.
    
    Paramètres :
        couts : matrice des coûts
        proposition : proposition initiale (modifiée en place)
        provisions, commandes : vecteurs de contraintes
        n, m : dimensions
    
    Retourne :
        proposition optimale
    """
    iteration = 0
    max_iterations = 1000  # Sécurité
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'#' * 70}")
        print(f"  ITÉRATION {iteration}")
        print(f"{'#' * 70}")
        
        # Afficher la proposition courante
        afficher_proposition(proposition, provisions, commandes, n, m,
                           f"PROPOSITION DE TRANSPORT - Itération {iteration}")
        
        # Coût total courant
        ct = cout_total(couts, proposition, n, m)
        print(f"  Coût total = {ct}")
        
        # Vérifier la non-dégénérescence
        est_non_degeneree(proposition, n, m)
        
        # Récupérer les arêtes de base
        aretes = aretes_base(proposition, n, m)
        
        # --- Test d'acyclicité ---
        print("\n  --- Test d'acyclicité ---")
        has_cycle, cycle_aretes = detecter_cycle_bfs(aretes, n, m)
        
        while has_cycle:
            print("  -> Maximisation sur le cycle détecté")
            proposition, delta, suppr = maximiser_transport_cycle(proposition, cycle_aretes, n, m)
            
            aretes = aretes_base(proposition, n, m)
            has_cycle, cycle_aretes = detecter_cycle_bfs(aretes, n, m)
            if has_cycle:
                print("  -> Autre cycle détecté, on recommence")
        
        print("  Proposition acyclique : OK")
        
        # --- Test de connexité ---
        print("\n  --- Test de connexité ---")
        aretes = aretes_base(proposition, n, m)
        est_connexe, composantes = test_connexite_bfs(aretes, n, m)
        
        if not est_connexe:
            proposition = rendre_connexe(proposition, couts, aretes, n, m, composantes)
            
            # Revérifier acyclicité après ajout
            aretes = aretes_base(proposition, n, m)
            has_cycle, cycle_aretes = detecter_cycle_bfs(aretes, n, m)
            while has_cycle:
                proposition, delta, suppr = maximiser_transport_cycle(proposition, cycle_aretes, n, m)
                aretes = aretes_base(proposition, n, m)
                has_cycle, cycle_aretes = detecter_cycle_bfs(aretes, n, m)
        
        # --- Calcul des potentiels ---
        print("\n  --- Calcul des potentiels ---")
        u, v = calculer_potentiels(couts, proposition, n, m)
        
        if None in u or None in v:
            print("  ERREUR : Potentiels non calculables (graphe non connexe ?)")
            print(f"  u = {u}")
            print(f"  v = {v}")
            break
        
        afficher_potentiels(u, v, n, m)
        
        # --- Coûts potentiels et marginaux ---
        print("  --- Tables des coûts potentiels et marginaux ---")
        marginaux, meilleure_arete, meilleur_marginal = afficher_table_potentiels_marginaux(
            couts, u, v, proposition, n, m)
        
        # --- Test d'optimalité ---
        if meilleure_arete is None:
            print("  *** SOLUTION OPTIMALE TROUVÉE ***")
            print(f"  Coût optimal = {ct}")
            break
        else:
            i_best, j_best = meilleure_arete
            print(f"  Arête améliorante : ({i_best+1}, {j_best+1}) avec marginal = {meilleur_marginal}")
            
            # Ajouter l'arête améliorante et trouver le cycle
            print("\n  --- Recherche du cycle ---")
            cycle = trouver_cycle_avec_arete(proposition, n, m, (i_best, j_best))
            
            if not cycle:
                print("  ERREUR : Impossible de trouver le cycle")
                break
            
            print(f"  Cycle trouvé : {[(i+1, j+1) for (i, j) in cycle]}")
            
            # Maximiser le transport sur ce cycle
            print("\n  --- Maximisation du transport ---")
            proposition, delta, suppr = maximiser_transport_cycle(proposition, cycle, n, m)
            
            if delta == 0:
                print("  delta = 0, dégénérescence")
    
    # Affichage final
    print(f"\n{'=' * 70}")
    print("  SOLUTION OPTIMALE")
    print(f"{'=' * 70}")
    afficher_proposition(proposition, provisions, commandes, n, m,
                        "PROPOSITION OPTIMALE")
    ct = cout_total(couts, proposition, n, m)
    print(f"  COÛT TOTAL OPTIMAL = {ct}")
    
    return proposition


# =============================================================================
# ÉTAPE 8 : GÉNÉRATION ALÉATOIRE DE PROBLÈMES DE TRANSPORT
# =============================================================================
# Pour l'étude de complexité, on génère des problèmes de taille n x n.
#
# Pseudo-code :
#   Pour chaque a_ij : aléatoire entre 1 et 100
#   Générer une matrice temp de taille n x n (aléatoire 1-100)
#   P_i = somme de la ligne i de temp
#   C_j = somme de la colonne j de temp
#   Ceci garantit sum(P_i) = sum(C_j) (problème équilibré)

def generer_probleme_aleatoire(taille_n):
    """
    Génère un problème de transport aléatoire équilibré de taille n x n.
    
    Retourne :
        n, m, couts, provisions, commandes
    """
    n = m = taille_n
    
    # Matrice des coûts : aléatoire entre 1 et 100
    couts = [[random.randint(1, 100) for _ in range(m)] for _ in range(n)]
    
    # Matrice temporaire pour générer provisions et commandes équilibrées
    temp = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]
    
    provisions = [sum(temp[i]) for i in range(n)]
    commandes = [sum(temp[i][j] for i in range(n)) for j in range(n)]
    
    return n, m, couts, provisions, commandes


# =============================================================================
# ÉTAPE 9 : MESURE DE COMPLEXITÉ
# =============================================================================
# Pour chaque taille n, on exécute 100 fois avec des problèmes aléatoires.
# On mesure :
#   - θ_NO(n) : temps Nord-Ouest
#   - θ_BH(n) : temps Balas-Hammer
#   - t_NO(n) : temps marche-pied après Nord-Ouest
#   - t_BH(n) : temps marche-pied après Balas-Hammer
#
# On trace les nuages de points et les enveloppes supérieures.

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
    resultats = {
        'tailles': tailles,
        'theta_NO': {},
        'theta_BH': {},
        't_NO': {},
        't_BH': {},
    }
    
    # Rediriger la sortie si silencieux
    if silencieux:
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
    
    for taille in tailles:
        print(f"\n=== Taille n = {taille} ===", file=sys.stderr)
        resultats['theta_NO'][taille] = []
        resultats['theta_BH'][taille] = []
        resultats['t_NO'][taille] = []
        resultats['t_BH'][taille] = []
        
        for rep in range(nb_repetitions):
            if rep % 10 == 0:
                print(f"  Répétition {rep+1}/{nb_repetitions}", file=sys.stderr)
            
            n, m, couts, provisions, commandes = generer_probleme_aleatoire(taille)
            
            # Mesure Nord-Ouest
            t0 = time.perf_counter()
            prop_no = nord_ouest(couts, provisions, commandes, n, m)
            t1 = time.perf_counter()
            resultats['theta_NO'][taille].append(t1 - t0)
            
            # Mesure Balas-Hammer
            t0 = time.perf_counter()
            prop_bh = balas_hammer(couts, provisions, commandes, n, m)
            t1 = time.perf_counter()
            resultats['theta_BH'][taille].append(t1 - t0)
            
            # Mesure marche-pied après Nord-Ouest
            prop_no_copy = deepcopy(prop_no)
            t0 = time.perf_counter()
            try:
                methode_marche_pied(couts, prop_no_copy, provisions, commandes, n, m)
            except Exception:
                pass
            t1 = time.perf_counter()
            resultats['t_NO'][taille].append(t1 - t0)
            
            # Mesure marche-pied après Balas-Hammer
            prop_bh_copy = deepcopy(prop_bh)
            t0 = time.perf_counter()
            try:
                methode_marche_pied(couts, prop_bh_copy, provisions, commandes, n, m)
            except Exception:
                pass
            t1 = time.perf_counter()
            resultats['t_BH'][taille].append(t1 - t0)
    
    if silencieux:
        sys.stdout.close()
        sys.stdout = old_stdout
    
    return resultats


# =============================================================================
# ÉTAPE 10 : CRÉATION DES FICHIERS .TXT DES 12 PROBLÈMES
# =============================================================================

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


def creer_fichier_probleme(num_probleme, dossier="problemes"):
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
    
    chemin = os.path.join(dossier, f"probleme{num_probleme}.txt")
    
    with open(chemin, 'w') as f:
        f.write(f"{n} {m}\n")
        for i in range(n):
            ligne = " ".join(str(c) for c in couts[i])
            f.write(f"{ligne} {provisions[i]}\n")
        f.write(" ".join(str(c) for c in commandes) + "\n")
    
    return chemin


def creer_tous_les_fichiers(dossier="problemes"):
    """Crée les 12 fichiers .txt."""
    for num in range(1, 13):
        chemin = creer_fichier_probleme(num, dossier)
        print(f"Fichier créé : {chemin}")


# =============================================================================
# PROGRAMME PRINCIPAL
# =============================================================================

def programme_principal():
    """
    Programme principal interactif.
    L'utilisateur choisit un problème, une méthode initiale,
    puis le programme résout et affiche la trace complète.
    """
    # Créer les fichiers des problèmes
    dossier = "problemes"
    creer_tous_les_fichiers(dossier)
    
    continuer = True
    while continuer:
        print("\n" + "=" * 70)
        print("  RÉSOLUTION DE PROBLÈMES DE TRANSPORT")
        print("=" * 70)
        
        # Choix du problème
        print("\nProblèmes disponibles : 1 à 12")
        try:
            num = int(input("Choisissez le numéro du problème (1-12) : "))
            if num < 1 or num > 12:
                print("Numéro invalide.")
                continue
        except ValueError:
            print("Entrée invalide.")
            continue
        
        # Lire le fichier
        chemin = os.path.join(dossier, f"probleme{num}.txt")
        n, m, couts, provisions, commandes = lire_fichier(chemin)
        
        # Vérifier l'équilibre
        total_prov = sum(provisions)
        total_cmd = sum(commandes)
        print(f"\nProblème {num} : {n} fournisseurs x {m} clients")
        print(f"Total provisions = {total_prov}, Total commandes = {total_cmd}")
        if total_prov != total_cmd:
            print("ERREUR : Problème non équilibré !")
            continue
        print("Problème équilibré : OK")
        
        # Afficher la matrice des coûts
        afficher_matrice_couts(couts, provisions, commandes, n, m)
        
        # Choix de la méthode initiale
        print("\nMéthodes de proposition initiale :")
        print("  1. Nord-Ouest (NO)")
        print("  2. Balas-Hammer (BH)")
        try:
            choix = int(input("Votre choix (1 ou 2) : "))
        except ValueError:
            choix = 1
        
        if choix == 2:
            print("\n--- Méthode Balas-Hammer ---")
            proposition = balas_hammer(couts, provisions, commandes, n, m)
            methode = "BH"
        else:
            print("\n--- Méthode Nord-Ouest ---")
            proposition = nord_ouest(couts, provisions, commandes, n, m)
            methode = "NO"
        
        # Afficher la proposition initiale
        afficher_proposition(proposition, provisions, commandes, n, m,
                           f"PROPOSITION INITIALE ({methode})")
        ct = cout_total(couts, proposition, n, m)
        print(f"  Coût de la proposition initiale = {ct}")
        
        # Résolution par marche-pied
        print("\n--- Méthode du marche-pied avec potentiel ---")
        proposition_opt = methode_marche_pied(couts, proposition, provisions, commandes, n, m)
        
        # Proposer de continuer
        rep = input("\nVoulez-vous tester un autre problème ? (o/n) : ")
        continuer = rep.lower().startswith('o')
    
    print("\nMerci d'avoir utilisé le programme !")


def executer_et_sauvegarder_trace(num_probleme, methode, dossier_problemes="problemes",
                                   dossier_traces="traces", groupe="X", equipe="Y"):
    """
    Exécute un problème et sauvegarde la trace dans un fichier .txt.
    
    Paramètres :
        num_probleme (int) : numéro du problème (1-12)
        methode (str) : "no" pour Nord-Ouest, "bh" pour Balas-Hammer
        groupe, equipe (str) : identifiants pour le nom du fichier
    """
    if not os.path.exists(dossier_traces):
        os.makedirs(dossier_traces)
    
    nom_fichier = f"{groupe}-{equipe}-trace{num_probleme}-{methode}.txt"
    chemin_trace = os.path.join(dossier_traces, nom_fichier)
    
    # Rediriger la sortie vers le fichier
    old_stdout = sys.stdout
    sys.stdout = open(chemin_trace, 'w', encoding='utf-8')
    
    # Lire le problème
    chemin = os.path.join(dossier_problemes, f"probleme{num_probleme}.txt")
    n, m, couts, provisions, commandes = lire_fichier(chemin)
    
    print(f"Problème {num_probleme} : {n} fournisseurs x {m} clients")
    print(f"Méthode initiale : {'Nord-Ouest' if methode == 'no' else 'Balas-Hammer'}")
    print(f"Total provisions = {sum(provisions)}, Total commandes = {sum(commandes)}")
    
    afficher_matrice_couts(couts, provisions, commandes, n, m)
    
    if methode == "bh":
        proposition = balas_hammer(couts, provisions, commandes, n, m)
    else:
        proposition = nord_ouest(couts, provisions, commandes, n, m)
    
    afficher_proposition(proposition, provisions, commandes, n, m,
                        f"PROPOSITION INITIALE ({'NO' if methode == 'no' else 'BH'})")
    ct = cout_total(couts, proposition, n, m)
    print(f"Coût de la proposition initiale = {ct}")
    
    proposition_opt = methode_marche_pied(couts, proposition, provisions, commandes, n, m)
    
    sys.stdout.close()
    sys.stdout = old_stdout
    
    print(f"Trace sauvegardée : {chemin_trace}")


def generer_toutes_les_traces(groupe="X", equipe="Y"):
    """Génère les 24 traces d'exécution (12 problèmes x 2 méthodes)."""
    dossier = "problemes"
    creer_tous_les_fichiers(dossier)
    
    for num in range(1, 13):
        for methode in ["no", "bh"]:
            print(f"Exécution problème {num} - {methode.upper()}...")
            executer_et_sauvegarder_trace(num, methode, groupe=groupe, equipe=equipe)


# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "traces":
            groupe = sys.argv[2] if len(sys.argv) > 2 else "X"
            equipe = sys.argv[3] if len(sys.argv) > 3 else "Y"
            generer_toutes_les_traces(groupe, equipe)
        elif sys.argv[1] == "complexite":
            tailles = [10, 40, 100]  # Réduire pour le test
            resultats = mesurer_complexite(tailles, nb_repetitions=10)
            print("Résultats :", resultats)
        elif sys.argv[1] == "test":
            # Test rapide sur le problème de l'exemple (problème de la figure 1.1)
            dossier = "problemes"
            creer_tous_les_fichiers(dossier)
            
            n, m, couts, provisions, commandes = lire_fichier(
                os.path.join(dossier, "probleme1.txt"))
            
            afficher_matrice_couts(couts, provisions, commandes, n, m)
            
            print("\n=== NORD-OUEST ===")
            prop_no = nord_ouest(couts, provisions, commandes, n, m)
            afficher_proposition(prop_no, provisions, commandes, n, m)
            print(f"Coût = {cout_total(couts, prop_no, n, m)}")
            
            print("\n=== BALAS-HAMMER ===")
            prop_bh = balas_hammer(couts, provisions, commandes, n, m)
            afficher_proposition(prop_bh, provisions, commandes, n, m)
            print(f"Coût = {cout_total(couts, prop_bh, n, m)}")
            
            print("\n=== MARCHE-PIED (depuis Nord-Ouest) ===")
            prop_opt = methode_marche_pied(couts, prop_no, provisions, commandes, n, m)
        else:
            programme_principal()
    else:
        programme_principal()
