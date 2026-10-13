from players import joueurs
from regles_morpion import trouver_gagnant


def afficher_grille(grille):
    print("\n")
    print(f" {grille[0]} | {grille[1]} | {grille[2]} ")
    print("---|---|---")
    print(f" {grille[3]} | {grille[4]} | {grille[5]} ")
    print("---|---|---")
    print(f" {grille[6]} | {grille[7]} | {grille[8]} ")
    print("\n")


def annoncer_fin(grille, resultat):
    afficher_grille(grille)
    print("\n==============================")
    print("          GREAT GAME")
    print("==============================")
    print(resultat)
    print("==============================\n")


def jouer_match_morpion():
    if len(joueurs) < 2:
        print("Il faut au moins 2 joueurs.")
        return

    grille = [" "] * 9
    joueur_actuel = "X"
    noms = [joueurs[0]["nom"], joueurs[1]["nom"]]

    while True:
        afficher_grille(grille)
        try:
            case = int(input(f"{noms[0 if joueur_actuel=='X' else 1]}, choisis une case (1-9) : ")) - 1
        except ValueError:
            print("Choix invalide.")
            continue

        if case < 0 or case > 8 or grille[case] != " ":
            print("Case invalide ou déjà prise.")
            continue

        grille[case] = joueur_actuel

        if trouver_gagnant(grille) is not None:
            annoncer_fin(grille, f"Le gagnant est : {noms[0 if joueur_actuel=='X' else 1]}")
            return

        if " " not in grille:
            annoncer_fin(grille, "Égalité !")
            return

        joueur_actuel = "O" if joueur_actuel=="X" else "X"
