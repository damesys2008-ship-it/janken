from players import JOUEURS_MINIMUM_PAR_MATCH
from regles_morpion import CASE_VIDE, NOMBRE_DE_CASES, trouver_gagnant
from resultats import EGALITE, PREMIER_GAGNE, SECOND_GAGNE, texte_resultat

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


def resultat_de_la_partie(grille, marque_actuelle):
    """Renvoie le résultat si la partie est terminée, sinon None."""
    if trouver_gagnant(grille) is not None:
        if marque_actuelle == MARQUE_PREMIER_JOUEUR:
            return PREMIER_GAGNE
        return SECOND_GAGNE
    if CASE_VIDE not in grille:
        return EGALITE
    return None


def jouer_partie_morpion(joueur1, joueur2):
    """Joue une partie (X = joueur1, O = joueur2) et renvoie le résultat (cf. resultats.py)."""
    noms_par_marque = {
        MARQUE_PREMIER_JOUEUR: joueur1["nom"],
        MARQUE_SECOND_JOUEUR: joueur2["nom"],
    }
    grille = [CASE_VIDE] * NOMBRE_DE_CASES
    marque_actuelle = MARQUE_PREMIER_JOUEUR

    while True:
        case = demander_case(grille, noms_par_marque[marque_actuelle])
        grille[case] = marque_actuelle

        resultat = resultat_de_la_partie(grille, marque_actuelle)
        if resultat is not None:
            annoncer_fin(grille, texte_resultat(resultat, joueur1, joueur2))
            return resultat

        marque_actuelle = marque_suivante(marque_actuelle)


def jouer_match_morpion(joueurs):
    """Joue une partie de morpion entre les deux premiers joueurs."""
    if len(joueurs) < JOUEURS_MINIMUM_PAR_MATCH:
        print(f"Il faut au moins {JOUEURS_MINIMUM_PAR_MATCH} joueurs.")
        return

    jouer_partie_morpion(joueurs[0], joueurs[1])
