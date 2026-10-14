import getpass
import random
from players import JOUEURS_MINIMUM_PAR_MATCH
from regles_ppc import EGALITE, PREMIER_GAGNE, determiner_gagnant

CHOIX_PAR_TOUCHE = {"p": "pierre", "f": "feuille", "c": "ciseaux"}


def demander_choix(nom_joueur):
    """Demande le choix d'un joueur (p/f/c), caché à l'écran"""
    while True:
        touche = getpass.getpass(f"{nom_joueur}, choisis [p] / [f] / [c] : ").lower()
        if touche in CHOIX_PAR_TOUCHE:
            return CHOIX_PAR_TOUCHE[touche]
        print("Choix invalide. Tape p, f ou c.")


def annoncer_resultat(premier, second, resultat):
    """Affiche l'égalité ou le nom du gagnant."""
    if resultat == EGALITE:
        print("Égalité !")
    elif resultat == PREMIER_GAGNE:
        print(f"Le gagnant est : {premier['nom']}")
    else:
        print(f"Le gagnant est : {second['nom']}")


def jouer_match_ppc(joueurs):
    """Fait s'affronter deux joueurs tirés au hasard à pierre-feuille-ciseaux."""
    if len(joueurs) < JOUEURS_MINIMUM_PAR_MATCH:
        print(f"Il faut au moins {JOUEURS_MINIMUM_PAR_MATCH} joueurs pour jouer.")
        return

    premier, second = random.sample(joueurs, 2)
    print(f"{premier['nom']} affronte {second['nom']} !")

    choix_premier = demander_choix(premier['nom'])
    choix_second = demander_choix(second['nom'])
    print(f"{premier['nom']} a choisi {choix_premier}")
    print(f"{second['nom']} a choisi {choix_second}")

    resultat = determiner_gagnant(choix_premier, choix_second)
    annoncer_resultat(premier, second, resultat)
