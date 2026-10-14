import getpass
import random
from players import joueurs
from regles_ppc import EGALITE, PREMIER_GAGNE, determiner_gagnant

def demander_choix(nom_joueur):
    """Demande le choix d'un joueur (p/f/c), caché à l'écran"""
    correspondance = {"p": "pierre", "f": "feuille", "c": "ciseaux"}
    while True:
        choix = getpass.getpass(f"{nom_joueur}, choisis [p] / [f] / [c] : ").lower()
        if choix in correspondance:
            return correspondance[choix]
        print("Choix invalide. Tape p, f ou c.")

def jouer_match_ppc():
    if len(joueurs) < 2:
        print("Il faut au moins 2 joueurs pour jouer.")
        return

    premier, second = random.sample(joueurs, 2)
    print(f"{premier['nom']} affronte {second['nom']} !")

    choix_premier = demander_choix(premier['nom'])
    choix_second = demander_choix(second['nom'])
    print(f"{premier['nom']} a choisi {choix_premier}")
    print(f"{second['nom']} a choisi {choix_second}")

    resultat = determiner_gagnant(choix_premier, choix_second)
    if resultat == EGALITE:
        print("Égalité !")
    elif resultat == PREMIER_GAGNE:
        print(f"Le gagnant est : {premier['nom']}")
    else:
        print(f"Le gagnant est : {second['nom']}")
