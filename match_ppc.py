import getpass
import random
from elo import appliquer_resultat
from players import JOUEURS_MINIMUM_PAR_MATCH
from regles_ppc import determiner_gagnant
from resultats import texte_resultat
from tournoi import JEU_PPC, PREMIER_TOUR

CHOIX_PAR_TOUCHE = {"p": "pierre", "f": "feuille", "c": "ciseaux"}


def demander_choix(nom_joueur):
    """Demande le choix d'un joueur (p/f/c), caché à l'écran"""
    while True:
        touche = getpass.getpass(f"{nom_joueur}, choisis [p] / [f] / [c] : ").lower()
        if touche in CHOIX_PAR_TOUCHE:
            return CHOIX_PAR_TOUCHE[touche]
        print("Choix invalide. Tape p, f ou c.")


def jouer_partie_ppc(joueur1, joueur2):
    """Joue une partie entre deux joueurs donnés et renvoie le résultat (cf. resultats.py)."""
    print(f"{joueur1['nom']} affronte {joueur2['nom']} !")

    choix_joueur1 = demander_choix(joueur1['nom'])
    choix_joueur2 = demander_choix(joueur2['nom'])
    print(f"{joueur1['nom']} a choisi {choix_joueur1}")
    print(f"{joueur2['nom']} a choisi {choix_joueur2}")

    resultat = determiner_gagnant(choix_joueur1, choix_joueur2)
    print(texte_resultat(resultat, joueur1, joueur2))
    return resultat


def jouer_match_ppc(joueurs):
    """Fait s'affronter deux joueurs tirés au hasard et met à jour leurs statistiques."""
    if len(joueurs) < JOUEURS_MINIMUM_PAR_MATCH:
        print(f"Il faut au moins {JOUEURS_MINIMUM_PAR_MATCH} joueurs pour jouer.")
        return

    premier, second = random.sample(joueurs, 2)
    resultat = jouer_partie_ppc(premier, second)
    match = {"joueur1": premier, "joueur2": second, "resultat": resultat, "tour": PREMIER_TOUR}
    appliquer_resultat(match, JEU_PPC)
