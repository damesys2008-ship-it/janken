from players import JOUEURS_MINIMUM_PAR_MATCH
from regles_morpion import CASE_VIDE, NOMBRE_DE_CASES, trouver_gagnant

MARQUE_PREMIER_JOUEUR = "X"
MARQUE_SECOND_JOUEUR = "O"


def afficher_grille(grille):
    """Affiche la grille de morpion."""
    print("\n")
    print(f" {grille[0]} | {grille[1]} | {grille[2]} ")
    print("---|---|---")
    print(f" {grille[3]} | {grille[4]} | {grille[5]} ")
    print("---|---|---")
    print(f" {grille[6]} | {grille[7]} | {grille[8]} ")
    print("\n")


def annoncer_fin(grille, resultat):
    """Affiche la grille finale puis le résultat de la partie."""
    afficher_grille(grille)
    print("\n==============================")
    print("          GREAT GAME")
    print("==============================")
    print(resultat)
    print("==============================\n")


def marque_suivante(marque):
    """Renvoie la marque du joueur qui joue après celle donnée."""
    if marque == MARQUE_PREMIER_JOUEUR:
        return MARQUE_SECOND_JOUEUR
    return MARQUE_PREMIER_JOUEUR


def demander_case(grille, nom):
    """Affiche la grille et redemande tant que la case choisie n'est pas libre.

    Renvoie l'indice de la case (0 à NOMBRE_DE_CASES - 1).
    """
    while True:
        afficher_grille(grille)
        try:
            case = int(input(f"{nom}, choisis une case (1-{NOMBRE_DE_CASES}) : ")) - 1
        except ValueError:
            print("Choix invalide.")
            continue

        if case < 0 or case >= NOMBRE_DE_CASES or grille[case] != CASE_VIDE:
            print("Case invalide ou déjà prise.")
            continue

        return case


def associer_noms_aux_marques(joueurs):
    """Le premier joueur de la liste joue X, le second joue O."""
    return {
        MARQUE_PREMIER_JOUEUR: joueurs[0]["nom"],
        MARQUE_SECOND_JOUEUR: joueurs[1]["nom"],
    }


def resultat_de_la_partie(grille, nom_dernier_joueur):
    """Renvoie le message de fin si la partie est terminée, sinon None."""
    if trouver_gagnant(grille) is not None:
        return f"Le gagnant est : {nom_dernier_joueur}"
    if CASE_VIDE not in grille:
        return "Égalité !"
    return None


def jouer_match_morpion(joueurs):
    """Joue une partie de morpion entre les deux premiers joueurs."""
    if len(joueurs) < JOUEURS_MINIMUM_PAR_MATCH:
        print(f"Il faut au moins {JOUEURS_MINIMUM_PAR_MATCH} joueurs.")
        return

    grille = [CASE_VIDE] * NOMBRE_DE_CASES
    noms_par_marque = associer_noms_aux_marques(joueurs)
    marque_actuelle = MARQUE_PREMIER_JOUEUR

    while True:
        nom_actuel = noms_par_marque[marque_actuelle]
        case = demander_case(grille, nom_actuel)
        grille[case] = marque_actuelle

        resultat = resultat_de_la_partie(grille, nom_actuel)
        if resultat is not None:
            annoncer_fin(grille, resultat)
            return

        marque_actuelle = marque_suivante(marque_actuelle)
